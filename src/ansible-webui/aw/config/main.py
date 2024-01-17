from os import environ
from importlib.metadata import version, PackageNotFoundError
from sys import stderr

from pytz import all_timezones

from aw.config.environment import ENVIRON_FALLBACK


def get_version() -> str:
    if 'AW_VERSION' in environ:
        return environ['AW_VERSION']

    try:
        return version('ansible-webui')

    except PackageNotFoundError:
        stderr.write('\x1b[1;33mWARNING: Module version could not be determined!\x1b[0m\n')
        return '0.0.0'


VERSION = get_version()


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
