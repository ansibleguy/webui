import signal
from os import getpid
from os import kill as os_kill
from sys import exit as sys_exit
from threading import Thread
from time import sleep, time

from gunicorn.arbiter import Arbiter

from base.threader import ThreadManager
from aw.utils.debug import log
from aw.config.hardcoded import RELOAD_INTERVAL
from aw.model.job import Job, JobExecution


class Scheduler:
    WAIT_TIME = 1

    def __init__(self):
        self.thread_manager = ThreadManager()
        self.stopping = False
        self.reloading = False

    def stop(self, signum=None):
        if not self.stopping:
            log('Stopping..', level=3)
            self._signum_log(signum=signum)
            self.stopping = True

            log('Stopping job-threads', level=6)
            self.thread_manager.stop()

            sleep(self.WAIT_TIME)
            log('Finished!')

    def reload(self, signum=None):
        if not self.reloading and not self.stopping:
            self.reloading = True

            if signum is not None:
                log('Reloading..', level=3)
                self._signum_log(signum=signum)

            # todo: add or remove job threads
            log('Reloading job-threads', level=6)

            self.reloading = False

    @staticmethod
    def _signum_log(signum):
        log(f'Scheduler got signal {signum}')

    def _thread(self, job: Job, execution: JobExecution = None):
        # todo: creation of execution object for ad-hoc execution (with user-provided values)
        self.thread_manager.add_thread(job=job, execution=execution)
        self.thread_manager.start_thread(job=job)

    def start(self):
        log('Starting..', level=3)

        # todo: add job threads
        log('Starting job-threads', level=4)

        self._run()

    def _run(self):
        # pylint: disable=W0718
        try:
            sleep(self.WAIT_TIME)
            log('Entering Scheduler runtime', level=7)
            run_last_reload_time = time()

            while True:
                if self.stopping:
                    return

                if time() > (run_last_reload_time + RELOAD_INTERVAL):
                    self.reload()
                    break

                sleep(1)

        except Exception as err:
            print(f'ERROR: {err}')
            self.stop()
            return


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
        os_kill(getpid(), signal.SIGQUIT)  # trigger 'Arbiter.stop'
        sleep(3)
        sys_exit(0)

    def signal_reload(signum=None, stack=None):
        del stack
        scheduler.reload(signum)

    signal.signal(signal.SIGHUP, signal_reload)
    signal.signal(signal.SIGINT, signal_exit)
    signal.signal(signal.SIGTERM, signal_exit)

    scheduler_thread.start()
