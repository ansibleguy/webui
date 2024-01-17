from datetime import datetime

from pytz import timezone

from aw.config.main import config


def datetime_w_tz() -> datetime:
    return timezone(config['timezone']).localize(datetime.now())


def get_choice_key_by_value(choices: list[tuple], value):
    for k, v in choices:
        if v == value:
            return k

    return None
