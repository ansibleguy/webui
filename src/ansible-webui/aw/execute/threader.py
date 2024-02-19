# runs service timers in multiple threads
# base code source: https://github.com/sankalpjonn/timeloop

from threading import Thread, Event
from time import sleep
import traceback

from aw.utils.debug import log
from aw.config.hardcoded import THREAD_JOIN_TIMEOUT
from aw.model.job import Job, JobExecution
from aw.execute.play import ansible_playbook
from aw.utils.handlers import AnsibleConfigError, AnsibleRepositoryError
from aw.utils.util import get_next_cron_execution_sec, get_next_cron_execution_str, is_set


class Workload(Thread):
    FAIL_SLEEP = 5
    MAX_CONFIG_INVALID = 3

    def __init__(self, job: Job, manager, name: str, execution: JobExecution, once: bool = False, daemon: bool = True):
        Thread.__init__(self, daemon=daemon, name=name)
        self.job = job
        self.execution = execution
        self.manager = manager
        self.once = once
        self.started = False
        self.stopped = False
        self.state_stop = Event()
        self.log_name_debug = f"'{self.job.name}' (Job-ID {self.job.id}; {self.name})"
        self.log_name = f"'{self.job.name}' (Job-ID {self.job.id})"
        self.next_execution_time = None
        self.config_invalid = 0

    def stop(self) -> bool:
        log(f"Thread stopping {self.log_name_debug}", level=6)
        self.state_stop.set()

        try:
            self.join(THREAD_JOIN_TIMEOUT)
            if self.is_alive():
                log(f"Unable to join thread {self.log_name_debug}", level=5)

        except RuntimeError:
            # 'cannot join current thread'
            pass

        log(f"Stopped thread {self.log_name_debug}", level=4)
        self.started = False
        self.stopped = True
        return True

    def run_playbook(self):
        ansible_playbook(job=self.job, execution=self.execution)

    def run(self, error: bool = False) -> None:
        if self.once and self.started:
            self.stop()
            return

        if self.stopped:
            return

        if self.config_invalid >= self.MAX_CONFIG_INVALID:
            self.next_execution_time = None
            self.job.enabled = False
            self.job.save()
            log(msg=f"Disabling job {self.log_name} because of invalid config! Please fix it", level=2)
            # exit loop because it will always fail; fixing the config will replace this threat instance
            return

        if error:
            sleep(self.FAIL_SLEEP)

        self.started = True
        log(f"Entering runtime of thread {self.log_name_debug}", level=7)
        try:
            if self.once:
                self.run_playbook()
                self.stop()
                self.manager.threads.remove(self)
                return

            while not self.state_stop.is_set():
                wait_sec = get_next_cron_execution_sec(self.job.schedule)
                self.next_execution_time = get_next_cron_execution_str(schedule=self.job.schedule, wait_sec=wait_sec)
                log(
                    f"Next execution of job {self.log_name_debug} at "
                    f"{self.next_execution_time}",
                    level=7,
                )

                while not self.state_stop.wait(wait_sec):
                    if self.state_stop.is_set():
                        log(f"Exiting thread {self.log_name_debug}", level=5)
                        break

                    log(f"Starting job {self.log_name_debug}", level=5)
                    self.run_playbook()
                    break

        except (AnsibleConfigError, AnsibleRepositoryError, OSError) as err:
            self.config_invalid += 1
            log(
                msg=f"Got invalid config/environment for job {self.log_name} "
                    f"({self.config_invalid}/{self.MAX_CONFIG_INVALID}): \"{err}\"",
                level=2,
            )
            self.run(error=True)

        # pylint: disable=W0718
        except Exception as err:
            tb = traceback.format_exc(limit=256)
            log(
                msg=f"Got unexpected error while executing job {self.log_name}: \"{err}\"\n{tb}",
                level=2,
            )
            self.run(error=True)


class ThreadManager:
    def __init__(self):
        self.threads = set()
        self.thread_nr = 0
        self.stopping = False

    def start(self) -> None:
        log('Starting all threads', level=6)

        for thread in self.threads:
            if not thread.started:
                thread.start()

    def add_thread(self, job: Job, execution: JobExecution = None, once: bool = False):
        schedule = f" with schedule \"{job.schedule}\"" if is_set(job.schedule) else ''
        log(f"Adding thread for \"{job.name}\"{schedule}", level=7)
        self.thread_nr += 1
        self.threads.add(
            Workload(
                job=job,
                execution=execution,
                manager=self,
                once=once,
                name=f"Thread #{self.thread_nr}",
            )
        )

    def stop(self) -> bool:
        if self.stopping:
            return False

        self.stopping = True
        log('Stopping all threads', level=6)

        thread_list = list(self.threads)
        thread_count = len(thread_list)
        for i in range(thread_count):
            _ = thread_list[i]
            self.threads.remove(_)

        log('All threads stopped', level=3)
        return True

    def stop_thread(self, job: Job):
        log(f"Stopping thread for \"{job.name}\"", level=6)
        for thread in self.threads:
            if thread.job == job:
                if thread.started:
                    thread.stop()
                    self.threads.remove(thread)
                    log(f"Thread '{job.name}' stopped.", level=4)
                    break

    def start_thread(self, job: Job) -> None:
        for thread in self.threads:
            if thread.job == job:
                if not thread.started and not thread.stopped:
                    thread.start()
                    log(f"Thread '{job.name}' started.", level=5)
                    break

    def replace_thread(self, job: Job) -> None:
        log(f"Replacing thread for \"{job.name}\"", level=6)
        self.stop_thread(job)
        self.add_thread(job)
        self.start_thread(job)

    def list(self) -> list[Job]:
        return [thread.job for thread in self.threads]

    def list_pretty(self) -> list:
        pretty = []
        for thread in self.threads:
            if thread.next_execution_time is None:
                next_run = 'None'
            else:
                next_run = thread.next_execution_time

            pretty.append(f'{thread.job.name} next run at {next_run}')

        return pretty

    def clean_stopped_threads(self):
        to_remove = []
        for thread in self.threads:
            if thread.stopped:
                to_remove.append(thread)

        for thread in to_remove:
            self.threads.remove(thread)

    def __del__(self):
        try:
            self.stop()

        except ImportError:
            pass
