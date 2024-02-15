from os import environ
from importlib.metadata import version, PackageNotFoundError
from sys import stderr

from pytz import all_timezones, timezone

from aw.config.environment import AW_ENV_VARS, get_aw_env_var
from aw.utils.util_no_config import set_timezone


def get_version() -> str:
    env_version = get_aw_env_var('version')
    if env_version is not None:
        return env_version

    try:
        return version('ansible-webui')

    except PackageNotFoundError:
        # NOTE: not able to use aw.utils.debug.log_warn because of circular dependency
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
    environ['ANSIBLE_FORCE_COLOR'] = '1'

    for cnf_key in AW_ENV_VARS:
        config[cnf_key] = get_aw_env_var(cnf_key)

    if config['timezone'] not in all_timezones:
        config['timezone'] = 'GMT'

    # todo: merge config from webUI
    # todo: grey-out settings that are provided via env-var in webUI form and show value

    set_timezone(config['timezone'])
    config['timezone'] = timezone(config['timezone'])


def check_config_is_true(var: str, fallback: bool = False) -> bool:
    val = config[var]
    if val is None:
        return fallback

    return str(val).lower() in ['1', 'true', 'y', 'yes']
