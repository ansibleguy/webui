from django.db import models
from django.core.exceptions import ObjectDoesNotExist

from aw.model.base import BaseModel, CHOICES_BOOL, DEFAULT_NONE
from aw.config.defaults import CONFIG_DEFAULTS
from aw.config.environment import check_aw_env_var_is_set


class SystemConfig(BaseModel):
    form_fields = [
        'path_run', 'path_play', 'path_log', 'timezone', 'run_timeout', 'session_timeout', 'path_ansible_config',
        'path_ssh_known_hosts', 'debug', 'logo_url',
    ]
    # NOTE: 'AW_DB' is needed to get this config from DB and 'AW_SECRET' cannot be saved because of security breach
    api_fields_write = form_fields
    api_fields_read_only = ['db', 'db_migrate', 'serve_static', 'deployment', 'version']

    path_run = models.CharField(max_length=500, default='/tmp/ansible-webui')
    path_play = models.CharField(max_length=500, default=None)
    path_log = models.CharField(max_length=500, default=None)
    timezone = models.CharField(max_length=300, default=CONFIG_DEFAULTS['timezone'])
    run_timeout = models.PositiveIntegerField(default=CONFIG_DEFAULTS['run_timeout'])
    session_timeout = models.PositiveIntegerField(default=CONFIG_DEFAULTS['session_timeout'])
    path_ansible_config = models.CharField(max_length=500, **DEFAULT_NONE)
    path_ssh_known_hosts = models.CharField(max_length=500, **DEFAULT_NONE)
    debug = models.BooleanField(default=False, choices=CHOICES_BOOL)
    logo_url = models.CharField(max_length=500, **DEFAULT_NONE)

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
        config_db = SystemConfig(
            path_play=CONFIG_DEFAULTS['path_play'],
            path_log=CONFIG_DEFAULTS['path_log'],
        )
        config_db.save()

    return config_db
