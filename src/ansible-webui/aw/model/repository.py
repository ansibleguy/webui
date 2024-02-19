from django.db import models

from aw.config.main import config
from aw.model.base import BaseModel, DEFAULT_NONE, CHOICES_BOOL
from aw.model.job_credential import JobGlobalCredentials
from aw.utils.util import get_choice_value_by_key

CHOICES_REPOSITORY = [
    (1, 'Static'),
    (2, 'Git'),
]


class Repository(BaseModel):
    form_fields = [
        'name', 'rtype', 'static_path', 'git_origin', 'git_branch', 'git_isolate', 'git_lfs',
        'git_hook_pre', 'git_hook_post', 'git_override_initialize', 'git_override_update',
    ]
    api_fields_read = form_fields.copy()
    api_fields_read.extend(['id', 'rtype_name'])
    api_fields_write = form_fields

    name = models.CharField(max_length=100)
    rtype = models.PositiveSmallIntegerField(choices=CHOICES_REPOSITORY)

    static_path = models.CharField(max_length=500, blank=True, null=True, default=config['path_play'])

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

    def __str__(self) -> str:
        if self.rtype_name == 'Git':
            isolated = 'isolated ' if self.git_isolate else ''
            return f"{self.rtype_name.capitalize()} {isolated}repository - origin {self.git_origin}:{self.git_branch}"

        return f"{self.rtype_name.capitalize()} repository - path {self.static_path}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name'], name='repo_name_unique')
        ]
