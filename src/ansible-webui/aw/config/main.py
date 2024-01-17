from os import environ
from importlib.metadata import version

from pytz import all_timezones

from aw.config.environment import ENVIRON_FALLBACK


VERSION = environ['AW_VERSION'] if 'AW_VERSION' in environ else version('ansible-webui')


def init_globals():
    # pylint: disable=W0601
    global config
    config = {}

    environ.setdefault('DJANGO_SETTINGS_MODULE', 'aw.settings')
    environ['PYTHONIOENCODING'] = 'utf8'
    environ['PYTHONUNBUFFERED'] = '1'

    for cnf_key, values in ENVIRON_FALLBACK.items():
        for env_key in values['keys']:
            if env_key in environ:
                config[cnf_key] = environ[env_key]

        if cnf_key not in config:
            config[cnf_key] = values['fallback']

    if config['timezone'] not in all_timezones:
        config['timezone'] = 'GMT'
