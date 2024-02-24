import signal
from os import environ
from os import kill as os_kill
from sys import exit as sys_exit
from threading import Thread, ThreadError
from time import sleep, time

from gunicorn.arbiter import Arbiter
from django.core.validators import ValidationError
from django.db.utils import OperationalError, IntegrityError

from aw.settings import DB_FILE
from aw.execute.threader import ThreadManager
from aw.utils.debug import log
from aw.utils.util import is_null
from aw.config.hardcoded import INTERVAL_CHECK, INTERVAL_RELOAD
from aw.model.job import Job, JobExecution, validate_cronjob
from aw.execute.queue import queue_get


class Scheduler:
    WAIT_TIME = 1

    def __init__(self):
        self.thread_manager = ThreadManager()
        self.stopping = False
        self.reloading = False

    def stop(self, signum=None, error: bool = False):
        if not self.stopping:
            log('Stopping..', level=3)
            self._signum_log(signum=signum)
            self.stopping = True

            log('Stopping job-threads', level=6)
            self.thread_manager.stop()

            sleep(self.WAIT_TIME)
            log('Finished!')

            # else gunicorn will not know it should die
            os_kill(int(environ['MAINPID']), signal.SIGTERM)

            # just in case
            if error or signum is not None:
                sys_exit(1)

            sys_exit(0)

    @staticmethod
    def _signum_log(signum):
        log(f'Scheduler got signal {signum}')

    def _add_thread(self, job: Job, execution: JobExecution = None, once: bool = False):
        self.thread_manager.add_thread(job=job, execution=execution, once=once)
        self.thread_manager.start_thread(job=job)

    def start(self):
        log('Starting..', level=3)
        log('Starting job-threads', level=4)
        try:
            self.reload()
            self._run()

        except (OperationalError, IntegrityError) as err:
            log(
                "Database has an unexpected state! "
                f"If you are fine with losing the existing config - delete the database file: {DB_FILE}\n"
                f"Error: {err}"
            )
            self.stop()

    def _run(self):
        # pylint: disable=W0718
        try:
            sleep(self.WAIT_TIME)
            log('Entering Scheduler runtime', level=7)
            time_last_check = time()
            time_last_reload = time()

            while True:
                try:
                    if self.stopping:
                        break

                    if time() > (time_last_check + INTERVAL_CHECK):
                        self.check()
                        time_last_check = time()

                    if time() > (time_last_reload + INTERVAL_RELOAD):
                        self.reload()
                        time_last_reload = time()

                    sleep(self.WAIT_TIME)

                except ThreadError as err:
                    log(msg=f'Got thread error: {err}', level=2)

        except Exception as err:
            log(msg=f'Got unexpected error: {err}', level=1)
            self.stop(error=True)
            return

    def status(self):
        log(msg=f"Running job-threads: {self.thread_manager.list_pretty()}", level=4)

    def check(self):
        log('Checking for queued jobs', level=7)
        while True:
            queue_item = queue_get()
            if queue_item is None:
                break

            job, user = queue_item

            log(f"Adding job-thread for queued job: '{job.name}' (triggered by user '{user.username}')", level=4)
            self._add_thread(job=job, execution=JobExecution(user=user, job=job, comment='Triggered'), once=True)

    def reload(self, signum=None):
        if not self.reloading and not self.stopping:
            self.reloading = True

            if signum is not None:
                log('Reloading..', level=3)
                self._signum_log(signum=signum)

            self._reload_action(**self._reload_check())
            self.thread_manager.clean_stopped_threads()
            self.reloading = False

    def _reload_action(self, added: list, removed: list, changed: list):
        any_changed = False

        log('Checking jobs for config-changes', level=7)
        if len(added) > 0:
            any_changed = True
            log(f"Adding job-threads: {[job.name for job in added]}", level=4)
            for job in added:
                self._add_thread(job=job)

        if len(removed) > 0:
            any_changed = True
            log(f"Removing job-threads: {[job.name for job in removed]}", level=4)
            for job in removed:
                self.thread_manager.stop_thread(job)

        if len(changed) > 0:
            any_changed = True
            log(f"Replacing job-threads: {[job.name for job in changed]}", level=4)
            for job in changed:
                self.thread_manager.replace_thread(job)

        if any_changed:
            sleep(1)  # wait for threads to initialize
            self.status()

    def _reload_check(self) -> dict:
        result = {'added': [], 'removed': [], 'changed': []}
        running = self.thread_manager.list()
        running_ids = [job.id for job in running]
        configured = Job.objects.all()
        configured_ids = [job.id for job in configured]

        for job in configured:
            if job.id not in running_ids:
                if is_null(job.schedule):
                    log(f"Ignoring job '{job.name}' because it has no schedule", level=6)
                    continue

                if not job.enabled:
                    log(f"Ignoring job '{job.name}' because it is disabled", level=6)
                    continue

                try:
                    validate_cronjob(job.schedule)
                    result['added'].append(job)

                except ValidationError:
                    log(f"Got invalid job schedule '{job.schedule}'", level=4)

            else:
                run_job = [run_job for run_job in running if run_job.id == job.id][0]
                for field in Job.CHANGE_FIELDS:
                    if getattr(run_job, field) != getattr(job, field):
                        if run_job.enabled and not job.enabled:
                            result['removed'].append(job)
                            log(f"Job '{job.name}' was disabled", level=6)
                            break

                        result['changed'].append(job)
                        log(f"Job '{job.name}' config changed", level=6)
                        break

        for job in running:
            if job.id not in configured_ids:
                result['removed'].append(job)

        return result


def init_scheduler():
    scheduler = Scheduler()
    scheduler_thread = Thread(target=scheduler.start)

    # override gunicorn signal handling to allow for graceful shutdown
    Arbiter.SIGNALS.remove(signal.SIGHUP)
    Arbiter.SIGNALS.remove(signal.SIGINT)
    Arbiter.SIGNALS.remove(signal.SIGTERM)

    def signal_exit(signum=None, stack=None):
        del stack
        scheduler.stop(signum)
        os_kill(int(environ['MAINPID']), signal.SIGQUIT)  # trigger 'Arbiter.stop'
        sleep(3)
        sys_exit(1)

    def signal_reload(signum=None, stack=None):
        del stack
        scheduler.reload(signum)

    signal.signal(signal.SIGHUP, signal_reload)
    signal.signal(signal.SIGINT, signal_exit)
    signal.signal(signal.SIGTERM, signal_exit)

    scheduler_thread.start()
