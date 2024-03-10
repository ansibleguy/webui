from platform import uname
from os import environ, getpid
from sys import exit as sys_exit
from pathlib import Path

from django import setup as django_setup
from yaml import safe_load as yaml_load
from yaml import YAMLError

from aw.config.main import init_config

environ['AW_INIT'] = '1'
init_config()

# pylint: disable=C0413,C0415
from aw.config.main import config
from aw.utils.debug import log_warn, log_error, log
from aw.config.hardcoded import MIN_SECRET_LEN, ENV_KEY_CONFIG
from aw.config.environment import AW_ENV_VARS_REV


def _check_for_bad_config():
    if 'AW_SECRET' not in environ:
        log_warn(
            "The environmental variable 'AW_SECRET' was not supplied! "
            "Job-secrets like passwords might not be loadable after restart."
        )

    secret_len = len(config['secret'])
    if secret_len < MIN_SECRET_LEN:
        log_error(f"The provided secret key is too short! ({secret_len}<{MIN_SECRET_LEN} characters)")
        sys_exit(1)


def _load_config_file():
    # read config file and write settings into env-vars
    if ENV_KEY_CONFIG not in environ:
        return

    config_file = environ[ENV_KEY_CONFIG]

    if not Path(config_file).is_file():
        log_warn(
            f"The provided config-file was not found or unreadable: {config_file}"
        )
        environ[ENV_KEY_CONFIG] = '0'
        return

    log(msg=f"Using config-file: {config_file}", level=4)

    with open(config_file, 'r', encoding='utf-8') as _config:
        try:
            yaml_config = yaml_load(_config.read())
            if not isinstance(yaml_config, dict):
                raise ValueError('Content is not a dictionary')

            for setting, value in yaml_config.items():
                if setting.startswith('AW_'):
                    setting_env = setting

                else:
                    setting_env = f'AW_{setting.upper()}'

                if setting_env not in AW_ENV_VARS_REV:
                    log(msg=f"Provided setting is invalid: {setting}", level=3)
                    continue

                if isinstance(value, dict):
                    environ[setting_env] = setting

                elif isinstance(value, list):
                    environ[setting_env] = ','.join(value)

                else:
                    environ[setting_env] = str(value)

        except (YAMLError, ValueError) as err:
            log_warn(f"The provided config-file could not be loaded: {config_file} - {err}")


def main():
    if uname().system.lower() != 'linux':
        raise SystemError('Currently only linux systems are supported!')

    _load_config_file()
    _check_for_bad_config()

    from db import install_or_migrate_db

    environ['MAINPID'] = str(getpid())
    install_or_migrate_db()

    django_setup()
    environ['AW_INIT'] = '0'

    from db import create_first_superuser, create_privileged_groups
    from webserver import init_webserver
    from aw.execute.scheduler import init_scheduler
    from aw.settings import AUTH_MODE

    log(msg=f"Using Auth-Mode: {AUTH_MODE}", level=4)

    create_first_superuser()
    create_privileged_groups()
    init_scheduler()
    init_webserver()
