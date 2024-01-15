from os import environ
from sys import stdout

from aw.config.hardcoded import ENV_KEY_DEPLOYMENT


def deployment_dev() -> bool:
    return ENV_KEY_DEPLOYMENT in environ and environ[ENV_KEY_DEPLOYMENT] == 'dev'


def deployment_staging() -> bool:
    return ENV_KEY_DEPLOYMENT in environ and environ[ENV_KEY_DEPLOYMENT] == 'dev'


def deployment_prod() -> bool:
    return not deployment_dev() and not deployment_staging()


def _print_warn(msg: str):
    stdout.write('\x1b[1;33mWARNING: ' + msg + '\x1b[0m\n')


def warn_if_development():
    if deployment_dev():
        _print_warn('Development mode!')

    elif deployment_staging():
        _print_warn('Staging mode!')
