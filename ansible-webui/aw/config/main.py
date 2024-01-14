from os import environ
from secrets import choice as random_choice
from string import digits, ascii_letters, punctuation
from datetime import datetime
from pytz import all_timezones


ENVIRON_FALLBACK = {
    'timezone': {'keys': ['AW_TIMEZONE', 'TZ'], 'fallback': datetime.now().astimezone().tzname()},
    '_secret': {
        'keys': ['AW_TIMEZONE'],
        'fallback': ''.join(random_choice(ascii_letters + digits + punctuation) for i in range(50))
    },
}


def init_globals():
    global config
    config = {}

    for cnf_key, values in ENVIRON_FALLBACK.items():
        for env_key in values['keys']:
            if env_key in environ:
                config[cnf_key] = environ[env_key]

        if cnf_key not in config:
            config[cnf_key] = values['fallback']

    if config['timezone'] not in all_timezones:
        config['timezone'] = 'GMT'
