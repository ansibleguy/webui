from datetime import datetime

from aw.config.main import config


def datetime_w_tz() -> datetime:
    return datetime.now(config['timezone'])


def get_choice_key_by_value(choices: list[tuple], value):
    for k, v in choices:
        if v == value:
            return k

    return None
