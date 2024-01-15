import signal
from platform import uname
from threading import Thread
from os import getpid
from os import kill as os_kill
from time import sleep
from sys import exit as sys_exit

# pylint: disable=E0401,C0413
from gunicorn.arbiter import Arbiter

from aw.config.main import init_globals

init_globals()

from base.webserver import create_webserver
from base.scheduler import Scheduler


def main():
    if uname().system.lower() != 'linux':
        raise SystemError('Currently only linux systems are supported!')

    scheduler = Scheduler()
    scheduler_thread = Thread(target=scheduler.start)
    webserver = create_webserver()

    # override gunicorn signal handling to allow for graceful shutdown
    def signal_exit(signum=None, stack=None):
        del stack
        scheduler.stop(signum)
        os_kill(getpid(), signal.SIGQUIT)  # trigger 'Arbiter.stop'
        sleep(3)
        sys_exit(0)

    def signal_reload(signum=None, stack=None):
        del stack
        scheduler.reload(signum)

    Arbiter.SIGNALS.remove(signal.SIGHUP)
    Arbiter.SIGNALS.remove(signal.SIGINT)
    Arbiter.SIGNALS.remove(signal.SIGTERM)

    signal.signal(signal.SIGHUP, signal_reload)
    signal.signal(signal.SIGINT, signal_exit)
    signal.signal(signal.SIGTERM, signal_exit)

    scheduler_thread.start()
    webserver.run()
