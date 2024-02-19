from platform import python_version
from datetime import datetime, timedelta
from time import time
from os import open as open_file
from pathlib import Path
from functools import lru_cache, wraps
from pkg_resources import get_distribution

from crontab import CronTab
from pytz import utc


from aw.config.main import config
from aw.config.hardcoded import SHORT_TIME_FORMAT
from aw.utils.util_no_config import set_timezone

# allow import from other modules
# pylint: disable=W0611
from aw.utils.util_no_config import is_set, is_null


def datetime_w_tz() -> datetime:
    return datetime.now(config.timezone)


def datetime_from_db(dt: (datetime, None)) -> (datetime, None):
    # datetime form db will always be UTC; convert it
    if not isinstance(dt, datetime):
        return None

    local_dt = dt.replace(tzinfo=utc).astimezone(config.timezone)
    return config.timezone.normalize(local_dt)


def datetime_from_db_str(dt: (datetime, None), fmt: str = SHORT_TIME_FORMAT) -> str:
    dt = datetime_from_db(dt)
    if not isinstance(dt, datetime):
        return ''

    return dt.strftime(fmt)


def get_next_cron_execution_sec(schedule: str) -> float:
    cron = CronTab(schedule)
    set_timezone(str(config.timezone))
    return cron.next(now=datetime_w_tz())


def get_next_cron_execution(schedule: str, wait_sec: (int, float) = None) -> datetime:
    if wait_sec is None:
        wait_sec = get_next_cron_execution_sec(schedule)

    return datetime.fromtimestamp(time() + wait_sec)


def get_next_cron_execution_str(schedule: str, wait_sec: (int, float) = None) -> str:
    return get_next_cron_execution(schedule, wait_sec).strftime(SHORT_TIME_FORMAT)


def _open_file_0600(path: (str, Path), flags):
    return open_file(path, flags, 0o600)


def write_file_0600(file: (str, Path), content: str):
    mode = 'w'
    if Path(file).is_file():
        mode = 'a'

    with open(file, mode, encoding='utf-8', opener=_open_file_0600) as _file:
        _file.write(content)


def _open_file_0640(path: (str, Path), flags):
    return open_file(path, flags, 0o640)


def write_file_0640(file: (str, Path), content: str):
    mode = 'w'
    if Path(file).is_file():
        mode = 'a'

    with open(file, mode, encoding='utf-8', opener=_open_file_0640) as _file:
        _file.write(content)


def get_ansible_versions() -> str:
    return (f"Python3: {python_version()} | "
            f"Ansible: {get_distribution('ansible').version} | "
            f"Ansible-Core: {get_distribution('ansible-core').version} | "
            f"Ansible-Runner: {get_distribution('ansible-runner').version} |"
            f"Ansible-WebUI: {config['version']}")


# source: https://realpython.com/lru-cache-python/
def timed_lru_cache(seconds: int, maxsize: int = 128):
    def wrapper_cache(func):
        func = lru_cache(maxsize=maxsize)(func)
        func.lifetime = timedelta(seconds=seconds)
        func.expiration = datetime.utcnow() + func.lifetime

        @wraps(func)
        def wrapped_func(*args, **kwargs):
            if datetime.utcnow() >= func.expiration:
                func.cache_clear()
                func.expiration = datetime.utcnow() + func.lifetime

            return func(*args, **kwargs)

        return wrapped_func

    return wrapper_cache


def get_choice_value_by_key(choices: list[tuple], find: any) -> (any, None):
    for k, v in choices:
        if k == find:
            return v

    return None


def get_choice_key_by_value(choices: list[tuple], find: any):
    for k, v in choices:
        if v == find:
            return k

    return None


def unset_or_null(data: dict, key: str) -> bool:
    return key not in data or is_null(data[key])
