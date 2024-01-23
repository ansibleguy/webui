from datetime import datetime
from time import time

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
