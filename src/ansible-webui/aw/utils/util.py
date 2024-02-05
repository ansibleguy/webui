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


def datetime_w_tz() -> datetime:
    return datetime.now(config['timezone'])


def datetime_from_db(dt: datetime) -> datetime:
    # datetime form db will always be UTC; convert it
    local_dt = dt.replace(tzinfo=utc).astimezone(config['timezone'])
    return config['timezone'].normalize(local_dt)


def get_choice_key_by_value(choices: list[tuple], value):
    for k, v in choices:
        if v == value:
            return k

    return None


def is_null(data) -> bool:
    if data is None:
        return True

    return str(data).strip() == ''


def is_set(data: str) -> bool:
    return not is_null(data)


def get_next_cron_execution_sec(schedule: str) -> float:
    cron = CronTab(schedule)
    set_timezone(str(config['timezone']))
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


def get_choice_by_value(choices: (tuple, list), value: any) -> (any, None):
    # tuple[tuple[int, any]]
    for choice in choices:
        if choice[0] == value:
            return choice[1]

    return None
