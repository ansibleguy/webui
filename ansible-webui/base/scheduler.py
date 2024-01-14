from time import sleep, time

from base.threader import Loop as Threader
from aw.utils.debug import log
from aw.config.hardcoded import RELOAD_INTERVAL

# NOTE: not able to use models here because of dependency on django-init
# from aw.model.job import Job


class Scheduler:
    WAIT_TIME = 1

    def __init__(self):
        self.threader = Threader()
        self.stopping = False
        self.reloading = False

    def stop(self, signum=None):
        if not self.stopping:
            log('Stopping..', level=3)
            self._signum_log(signum=signum)
            self.stopping = True

            log('Stopping job-threads', level=6)
            self.threader.stop()

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

    def _thread(self, job):
        self.threader.add_thread(job)
        self.threader.start_thread(job)

    def start(self):
        log('Starting..', level=3)

        # todo: add job threads
        log('Starting job-threads', level=4)

        self._run()

    def _run(self):
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
