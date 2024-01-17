import signal
from os import getpid
from os import kill as os_kill
from time import sleep
from sys import exit as sys_exit
from threading import Thread
from platform import uname

# pylint: disable=E0401,C0413
from gunicorn.arbiter import Arbiter
from django import setup as django_setup

from aw.config.main import init_globals

init_globals()

from base.webserver import init_webserver


def main():
    if uname().system.lower() != 'linux':
        raise SystemError('Currently only linux systems are supported!')

    django_setup()

    init_scheduler()
    init_webserver()


def init_scheduler():
    # pylint: disable=C0415
    from base.scheduler import Scheduler
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
