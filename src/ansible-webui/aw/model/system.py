from pytz import all_timezones
from django.db import models
from django.core.exceptions import ObjectDoesNotExist

from aw.model.base import BaseModel, CHOICES_BOOL
from aw.config.defaults import CONFIG_DEFAULTS
from aw.config.environment import check_aw_env_var_is_set
from aw.utils.deployment import deployment_dev


class SystemConfig(BaseModel):
    form_fields = [
        'path_run', 'path_play', 'path_log', 'timezone', 'run_timeout', 'session_timeout', 'path_ansible_config',
        'path_ssh_known_hosts', 'debug',
    ]
    # NOTE: 'AW_DB' is needed to get this config from DB and 'AW_SECRET' cannot be saved because of security breach
    api_fields_write = form_fields
    api_fields_read_only = ['db', 'db_migrate', 'serve_static', 'deployment', 'version']

    path_run = models.CharField(max_length=500, default=CONFIG_DEFAULTS['path_run'])
    path_play = models.CharField(max_length=500, default=CONFIG_DEFAULTS['path_play'])
    path_log = models.CharField(max_length=500, default=CONFIG_DEFAULTS['path_log'])
    tz_choices = [(tz, tz) for tz in sorted(all_timezones)]
    timezone = models.CharField(
        max_length=300, choices=tz_choices, default=CONFIG_DEFAULTS['timezone'],
    )
    run_timeout = models.PositiveIntegerField(default=CONFIG_DEFAULTS['run_timeout'])
    session_timeout = models.PositiveIntegerField(default=CONFIG_DEFAULTS['session_timeout'])
    path_ansible_config = models.CharField(
        max_length=500, default=CONFIG_DEFAULTS['path_ansible_config'], null=True, blank=True,
    )
    path_ssh_known_hosts = models.CharField(
        max_length=500, default=CONFIG_DEFAULTS['path_ssh_known_hosts'], null=True, blank=True,
    )
    debug = models.BooleanField(default=CONFIG_DEFAULTS['debug'] or deployment_dev(), choices=CHOICES_BOOL)

    @classmethod
    def get_set_env_vars(cls) -> list:
        # grey-out settings in web-ui
        return [field for field in cls.form_fields if check_aw_env_var_is_set(field)]

    def __str__(self) -> str:
        return 'Ansible-WebUI System Config'


def get_config_from_db() -> SystemConfig:
    try:
        config_db = SystemConfig.objects.all().first()
        if config_db is None:
            raise ObjectDoesNotExist()

    except ObjectDoesNotExist:
        config_db = SystemConfig()
        config_db.save()

    return config_db
