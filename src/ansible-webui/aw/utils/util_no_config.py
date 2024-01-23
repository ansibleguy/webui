from os import environ
from time import tzset


def set_timezone(timezone: str):
    environ['TZ'] = timezone
    environ.setdefault('TZ', timezone)
    tzset()
