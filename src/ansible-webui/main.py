from platform import uname
from os import environ, getpid

from django import setup as django_setup

from aw.config.main import init_globals

init_globals()

# pylint: disable=C0413,C0415
from db import install_or_migrate_db


def main():
    if uname().system.lower() != 'linux':
        raise SystemError('Currently only linux systems are supported!')

    environ['MAINPID'] = str(getpid())
    install_or_migrate_db()

    django_setup()

    from db import create_first_superuser
    from webserver import init_webserver
    from aw.execute.scheduler import init_scheduler

    create_first_superuser()
    init_scheduler()
    init_webserver()
