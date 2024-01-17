from platform import uname

from django import setup as django_setup

from aw.config.main import init_globals

init_globals()


def main():
    if uname().system.lower() != 'linux':
        raise SystemError('Currently only linux systems are supported!')

    django_setup()

    # pylint: disable=C0415
    from base.webserver import init_webserver
    from base.scheduler import init_scheduler

    init_scheduler()
    init_webserver()
