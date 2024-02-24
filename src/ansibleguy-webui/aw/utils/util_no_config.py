from os import environ
from time import tzset


def set_timezone(timezone: str):
    environ['TZ'] = timezone
    environ.setdefault('TZ', timezone)
    tzset()


def is_null(data) -> bool:
    if data is None:
        return True

    return str(data).strip() == ''


def is_set(data: str) -> bool:
    return not is_null(data)
