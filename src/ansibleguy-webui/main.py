from platform import uname
from os import environ, getpid
from sys import exit as sys_exit

from django import setup as django_setup

from aw.config.main import init_config

init_config()

# pylint: disable=C0413,C0415
from aw.config.main import config
from aw.utils.debug import log_warn, log_error
from aw.config.hardcoded import MIN_SECRET_LEN

from db import install_or_migrate_db


def _check_for_bad_config():
    if 'AW_SECRET' not in environ:
        log_warn(
            "The environmental variable 'AW_SECRET' was not supplied! "
            "Job-secrets like passwords might not be loadable after restart."
        )

    secret_len = len(config['secret'])
    if secret_len < MIN_SECRET_LEN:
        log_error(f"The provided secret key is too short! ({secret_len}<{MIN_SECRET_LEN} characters)")
        sys_exit(1)


def main():
    if uname().system.lower() != 'linux':
        raise SystemError('Currently only linux systems are supported!')

    _check_for_bad_config()

    environ['AW_INIT'] = '1'
    environ['MAINPID'] = str(getpid())
    install_or_migrate_db()

    django_setup()
    environ['AW_INIT'] = '0'

    from db import create_first_superuser, create_privileged_groups
    from webserver import init_webserver
    from aw.execute.scheduler import init_scheduler

    create_first_superuser()
    create_privileged_groups()
    init_scheduler()
    init_webserver()
