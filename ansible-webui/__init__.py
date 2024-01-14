#!/usr/bin/env python3


if __name__ == '__main__':
    import signal
    from platform import uname
    from threading import Thread
    from os import getpid, environ
    from os import kill as os_kill
    from time import sleep

    from gunicorn.arbiter import Arbiter

    from aw.config.main import init_globals
    init_globals()

    from base.webserver import create_webserver
    from base.scheduler import Scheduler

    if uname().system.lower() != 'linux':
        raise SystemError('Currently only linux systems are supported!')

    scheduler = Scheduler()
    schedulerThread = Thread(target=scheduler.start)
    webserver = create_webserver()

    # override gunicorn signal handling to allow for graceful shutdown
    def signal_exit(signum=None, stack=None):
        scheduler.stop(signum)
        os_kill(getpid(), signal.SIGQUIT)  # trigger 'Arbiter.stop'
        sleep(5)
        exit(0)

    def signal_reload(signum=None, stack=None):
        scheduler.reload(signum)

    Arbiter.SIGNALS.remove(signal.SIGHUP)
    Arbiter.SIGNALS.remove(signal.SIGINT)
    Arbiter.SIGNALS.remove(signal.SIGTERM)

    signal.signal(signal.SIGHUP, signal_reload)
    signal.signal(signal.SIGINT, signal_exit)
    signal.signal(signal.SIGTERM, signal_exit)

    schedulerThread.start()
    webserver.run()
