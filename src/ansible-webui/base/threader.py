# runs service timers in multiple threads
# base code source: https://github.com/sankalpjonn/timeloop

from threading import Thread, Event

from crontab import CronTab

from aw.utils.debug import log
from aw.config import hardcoded
from aw.model.job import Job, JobExecution
from aw.execute.play import ansible_playbook


class Workload(Thread):
    def __init__(self, job: Job, manager, name: str, execution: JobExecution, once: bool = False, daemon: bool = True):
        Thread.__init__(self, daemon=daemon, name=name)
        self.job = job
        self.execution = execution
        self.manager = manager
        self.once = once
        self.started = False
        self.state_stop = Event()
        self.log_name = f"\"{self.name}\" (\"{self.job.name}\")"
        self.cron = CronTab(job.schedule)

    def stop(self) -> bool:
        log(f"Thread stopping {self.log_name}", level=6)
        self.state_stop.set()

        try:
            self.join(hardcoded.THREAD_JOIN_TIMEOUT)
            if self.is_alive():
                log(f"Unable to join thread {self.log_name}", level=5)

        except RuntimeError:
            log(f"Got error stopping thread {self.log_name}", level=5)

        log(f"Stopped thread {self.log_name}", level=4)
        self.started = False
        return True

    def run_playbook(self):
        ansible_playbook(job=self.job, execution=self.execution)

    def run(self) -> None:
        self.started = True
        log(f"Entering runtime of thread {self.log_name}", level=7)
        try:
            if self.once:
                self.run_playbook()
                self.stop()
                self.manager.threads.remove(self.job)
                return

            wait_sec = self.cron.next()
            log(f"Next execution of job {self.log_name} in {wait_sec}s", level=7)
            while not self.state_stop.wait(wait_sec):
                if self.state_stop.is_set():
                    log(f"Exiting thread {self.log_name}", level=5)
                    break

                log(f"Starting job {self.log_name}", level=5)
                self.run_playbook()

        except ValueError as err:
            log(f"Got unexpected error while executing job {self.log_name}: '{err}'")
            self.run()


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
        log(f"Adding thread for \"{job.name}\" with schedule \"{job.schedule}\"", level=7)
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
            del _

        log('All threads stopped', level=3)
        return True

    def stop_thread(self, job: Job):
        log(f"Stopping thread for \"{job.name}\"", level=6)
        for thread in self.threads:
            if thread.job.job_id == job.job_id:
                if thread.started:
                    thread.stop()
                    self.threads.remove(job)
                    log(f"Thread {job.name} stopped.", level=4)
                    del job
                    break

    def start_thread(self, job: Job) -> None:
        for thread in self.threads:
            if thread.job.job_id == job.job_id:
                if not thread.started:
                    thread.start()
                    log(f"Thread {job.name} started.", level=5)
                    break

    def replace_thread(self, job: Job) -> None:
        log(f"Reloading thread for \"{job.name}\"", level=6)
        self.stop_thread(job)
        self.add_thread(job)
        self.start_thread(job)

    def list(self) -> list:
        log('Returning thread list', level=8)
        return [thread.job.name for thread in self.threads]

    def __del__(self):
        try:
            self.stop()

        except ImportError:
            pass
