from datetime import datetime

from pytz import timezone

from aw.config.main import config


def datetime_w_tz() -> datetime:
    return timezone(config['timezone']).localize(datetime.now())
