from os import environ

from pytz import all_timezones

from aw.config.environment import ENVIRON_FALLBACK


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
