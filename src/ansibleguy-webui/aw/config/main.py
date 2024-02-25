from os import environ
from importlib.metadata import version, PackageNotFoundError
from sys import stderr

from pytz import all_timezones, timezone, BaseTzInfo
from django.db.utils import IntegrityError, OperationalError
from django.core.exceptions import ImproperlyConfigured, AppRegistryNotReady

from aw.config.environment import get_aw_env_var, get_aw_env_var_or_default
from aw.utils.util_no_config import set_timezone, is_set
from aw.config.defaults import CONFIG_DEFAULTS


def __get_module_version() -> str:
    env_version = get_aw_env_var_or_default('version')
    if env_version is not None:
        return env_version

    try:
        return version('ansibleguy-webui')

    except PackageNotFoundError:
        # NOTE: not able to use aw.utils.debug.log_warn because of circular dependency
        stderr.write('\x1b[1;33mWARNING: Module version could not be determined!\x1b[0m\n')
        return '0.0.0'


VERSION = __get_module_version()


class Config:
    def __init__(self):
        set_timezone(self.get('timezone'))

    @staticmethod
    def _from_env_or_db(setting: str) -> any:
        env_var_value = get_aw_env_var(setting)
        if is_set(env_var_value):
            return env_var_value

        try:
            if 'AW_INIT' in environ and environ['AW_INIT'] == '1':
                # do not try to use ORM before django-init
                raise AppRegistryNotReady

            # pylint: disable=C0415
            from aw.model.system import get_config_from_db
            value = getattr(get_config_from_db(), str(setting))
            if value is not None:
                return value

        except (IntegrityError, OperationalError, ImproperlyConfigured, AppRegistryNotReady, ImportError,
                AttributeError):
            # if database not initialized or migrations missing; or env-only var
            pass

        if setting not in CONFIG_DEFAULTS:
            return None

        return CONFIG_DEFAULTS[setting]

    def get(self, setting: str) -> any:
        return self._from_env_or_db(setting)

    def __getitem__(self, setting):
        return self._from_env_or_db(setting)

    @property
    def timezone(self) -> BaseTzInfo:
        tz_str = self.get('timezone')

        if tz_str not in all_timezones:
            return timezone('GMT')

        return timezone(tz_str)

    def is_true(self, setting: str, fallback: bool = False) -> bool:
        val = self.get(setting)
        if val is None:
            return fallback

        if isinstance(val, bool):
            return val

        return str(val).lower() in ['1', 'true', 'y', 'yes']


def init_config():
    environ.setdefault('DJANGO_SETTINGS_MODULE', 'aw.settings')
    environ['PYTHONIOENCODING'] = 'utf8'
    environ['PYTHONUNBUFFERED'] = '1'
    environ['ANSIBLE_FORCE_COLOR'] = '1'

    # pylint: disable=W0601
    global config
    config = Config()
