import signal
from os import environ
from os import kill as os_kill
from sys import exit as sys_exit
from time import sleep

from gunicorn.arbiter import Arbiter
from django.db.utils import IntegrityError, OperationalError
from django.core.exceptions import ImproperlyConfigured, AppRegistryNotReady

from aw.utils.debug import log


def handle_signals(scheduler):
    # override gunicorn signal handling to allow for graceful shutdown
    Arbiter.SIGNALS.remove(signal.SIGHUP)
    Arbiter.SIGNALS.remove(signal.SIGINT)
    Arbiter.SIGNALS.remove(signal.SIGTERM)

    def signal_exit(signum=None, stack=None):
        del signum, stack
        scheduler.stop()

        log('Stopping webserver..')
        os_kill(int(environ['MAINPID']), signal.SIGQUIT)  # trigger 'Arbiter.stop'
        sleep(3)

        try:
            # pylint: disable=C0415
            log('Closing database..')
            from django.db import connections
            connections.close_all()

        except (IntegrityError, OperationalError, ImproperlyConfigured, AppRegistryNotReady, ImportError):
            pass

        log('Gracefully stopped - Goodbye!')
        sys_exit(0)

    def signal_reload(signum=None, stack=None):
        del stack
        scheduler.reload(signum)

    signal.signal(signal.SIGHUP, signal_reload)
    signal.signal(signal.SIGINT, signal_exit)
    signal.signal(signal.SIGTERM, signal_exit)
