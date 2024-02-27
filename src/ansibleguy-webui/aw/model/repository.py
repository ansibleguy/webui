from django.db import models

from aw.config.main import config
from aw.config.hardcoded import SHORT_TIME_FORMAT
from aw.model.base import BaseModel, DEFAULT_NONE, CHOICES_BOOL, CHOICES_JOB_EXEC_STATUS
from aw.model.job_credential import JobGlobalCredentials
from aw.utils.util import get_choice_value_by_key, get_choice_key_by_value, datetime_from_db_str, is_null

CHOICES_REPOSITORY = [
    (1, 'Static'),
    (2, 'Git'),
]


class Repository(BaseModel):
    form_fields = [
        'name', 'rtype', 'static_path', 'git_origin', 'git_credentials', 'git_branch', 'git_isolate', 'git_lfs',
        'git_limit_depth', 'git_hook_pre', 'git_hook_post', 'git_override_initialize', 'git_override_update',
        'git_playbook_base',
    ]
    api_fields_read = form_fields.copy()
    api_fields_read.extend([
        'id', 'rtype_name', 'time_update', 'status', 'status_name', 'log_stdout', 'log_stdout_url',
        'log_stderr', 'log_stderr_url',

    ])
    api_fields_write = form_fields

    name = models.CharField(max_length=100, null=False, blank=False)
    rtype = models.PositiveSmallIntegerField(choices=CHOICES_REPOSITORY)
    time_update = models.DateTimeField(**DEFAULT_NONE)
    status = models.PositiveSmallIntegerField(default=0, choices=CHOICES_JOB_EXEC_STATUS)
    log_stdout = models.CharField(max_length=300, **DEFAULT_NONE)
    log_stderr = models.CharField(max_length=300, **DEFAULT_NONE)

    static_path = models.CharField(max_length=500, **DEFAULT_NONE)

    git_origin = models.CharField(max_length=100, **DEFAULT_NONE)
    git_branch = models.CharField(max_length=100, **DEFAULT_NONE)
    git_isolate = models.BooleanField(choices=CHOICES_BOOL, default=False)
    git_lfs = models.BooleanField(choices=CHOICES_BOOL, default=False)
    git_limit_depth = models.PositiveIntegerField(**DEFAULT_NONE)
    git_hook_pre = models.CharField(max_length=1000, **DEFAULT_NONE)
    git_hook_post = models.CharField(max_length=1000, **DEFAULT_NONE)
    git_override_initialize = models.CharField(max_length=1000, **DEFAULT_NONE)
    git_override_update = models.CharField(max_length=1000, **DEFAULT_NONE)
    git_playbook_base = models.CharField(max_length=300, **DEFAULT_NONE)
    git_credentials = models.ForeignKey(
        JobGlobalCredentials, on_delete=models.SET_NULL, related_name='repo_fk_cred', null=True, blank=True,
    )

    @property
    def rtype_name(self) -> str:
        return self.rtype_name_from_id(self.rtype)

    @staticmethod
    def rtype_name_from_id(rtype) -> str:
        return get_choice_value_by_key(choices=CHOICES_REPOSITORY, find=rtype)

    @property
    def time_update_str(self) -> str:
        if is_null(self.time_update):
            return ''

        return datetime_from_db_str(dt=self.time_update, fmt=SHORT_TIME_FORMAT) + f" {config['timezone']}"

    @property
    def status_name(self) -> str:
        return self.status_name_from_id(self.status)

    @staticmethod
    def status_name_from_id(rtype) -> str:
        return get_choice_value_by_key(choices=CHOICES_JOB_EXEC_STATUS, find=rtype)

    @staticmethod
    def status_id_from_name(name: str) -> int:
        return get_choice_key_by_value(choices=CHOICES_JOB_EXEC_STATUS, find=name)

    @property
    def log_stdout_url(self) -> str:
        return f"/api/repository/log/{self.id}?type=stdout"

    @property
    def log_stderr_url(self) -> str:
        return f"/api/repository/log/{self.id}?type=stderr"

    def __str__(self) -> str:
        if self.rtype_name == 'Git':
            isolated = 'isolated ' if self.git_isolate else ''
            return f"{self.rtype_name.capitalize()} {isolated}repository - origin {self.git_origin}:{self.git_branch}"

        return f"{self.rtype_name.capitalize()} repository - path {self.static_path}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name'], name='repo_name_unique'),
        ]
