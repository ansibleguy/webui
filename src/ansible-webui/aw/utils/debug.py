from os import getpid
from sys import stderr, stdout

from aw.utils.util import datetime_w_tz
from aw.utils.deployment import deployment_dev, deployment_staging
from aw.config.hardcoded import LOG_TIME_FORMAT

PID = getpid()

LEVEL_NAME_MAPPING = {
    1: 'FATAL',
    2: 'ERROR',
    3: 'WARN',
    4: 'INFO',
    5: 'INFO',
    6: 'DEBUG',
    7: 'DEBUG',
}


def _log_prefix() -> str:
    # time format adapted to the one used by gunicorn
    # todo: update gunicorn log format (gunicorn.glogging.CONFIG_DEFAULTS)
    return f'[{datetime_w_tz().strftime(LOG_TIME_FORMAT)}] [{PID}]'


def log(msg: str, level: int = 3):
    if level > 5 and not deployment_dev():
        return

    print(f"{_log_prefix()} [{LEVEL_NAME_MAPPING[level]}] {msg}")


def log_warn(msg: str, _stderr: bool = False):
    if _stderr:
        stderr.write(f'\x1b[1;33m{_log_prefix()} [{LEVEL_NAME_MAPPING[3]}] {msg}\x1b[0m\n')

    else:
        stdout.write(f'\x1b[1;33m{_log_prefix()} [{LEVEL_NAME_MAPPING[3]}] {msg}\x1b[0m\n')


def log_error(msg: str):
    stderr.write(f'\033[01;{_log_prefix()} [{LEVEL_NAME_MAPPING[2]}] {msg}\x1b[0m\n')


def warn_if_development():
    if deployment_dev():
        log_warn('Development mode!')

    elif deployment_staging():
        log_warn('Staging mode!')
