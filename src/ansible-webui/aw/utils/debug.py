from os import getpid

from aw.utils.util import datetime_w_tz
from aw.utils.deployment import deployment_dev
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


def log(msg: str, level: int = 3):
    if level > 5 and not deployment_dev():
        return

    # time format adapted to the one used by gunicorn
    print(f"[{datetime_w_tz().strftime(LOG_TIME_FORMAT)}] [{PID}] [{LEVEL_NAME_MAPPING[level]}] {msg}")
