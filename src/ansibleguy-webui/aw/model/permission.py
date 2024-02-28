from django.db import models

from aw.model.base import BareModel, BaseModel, CHOICES_BOOL
from aw.model.job import Job
from aw.model.job_credential import JobGlobalCredentials
from aw.model.repository import Repository
from aw.base import USERS, GROUPS
from aw.utils.util import get_choice_value_by_key

CHOICE_PERMISSION_READ = 5
CHOICE_PERMISSION_EXECUTE = 10
CHOICE_PERMISSION_WRITE = 15
CHOICE_PERMISSION_FULL = 20
CHOICE_PERMISSION_DELETE = CHOICE_PERMISSION_FULL
CHOICES_PERMISSION = [
    (0, 'None'),
    (CHOICE_PERMISSION_READ, 'Read'),
    (CHOICE_PERMISSION_EXECUTE, 'Execute'),
    (CHOICE_PERMISSION_WRITE, 'Write'),
    (CHOICE_PERMISSION_FULL, 'Full'),
]


class JobPermission(BaseModel):
    form_fields = [
        'name', 'permission', 'users', 'groups', 'jobs', 'jobs_all', 'credentials', 'credentials_all',
        'repositories', 'repositories_all',
    ]
    api_fields_write = form_fields
    api_fields_read = ['permission_name', 'jobs_name', 'credentials_name', 'users_name', 'groups_name']
    api_fields_read.extend(form_fields)

    name = models.CharField(max_length=100, null=False, blank=False)
    permission_default = 0
    permission = models.PositiveSmallIntegerField(choices=CHOICES_PERMISSION, default=permission_default)
    users = models.ManyToManyField(
        USERS,
        through='JobPermissionMemberUser',
        through_fields=('permission', 'user'),
    )
    groups = models.ManyToManyField(
        GROUPS,
        through='JobPermissionMemberGroup',
        through_fields=('permission', 'group'),
    )
    jobs = models.ManyToManyField(
        Job,
        through='JobPermissionMapping',
        through_fields=('permission', 'job'),
    )
    jobs_all = models.BooleanField(choices=CHOICES_BOOL, default=False)
    credentials = models.ManyToManyField(
        JobGlobalCredentials,
        through='JobCredentialsPermissionMapping',
        through_fields=('permission', 'credentials'),
    )
    credentials_all = models.BooleanField(choices=CHOICES_BOOL, default=False)
    repositories = models.ManyToManyField(
        Repository,
        through='JobRepositoryPermissionMapping',
        through_fields=('permission', 'repository'),
    )
    repositories_all = models.BooleanField(choices=CHOICES_BOOL, default=False)

    @property
    def permission_name(self) -> str:
        return self.permission_name_from_id(self.permission)

    @staticmethod
    def permission_name_from_id(permission) -> str:
        return get_choice_value_by_key(choices=CHOICES_PERMISSION, find=permission)

    def __str__(self) -> str:
        return f"Permission '{self.name}' - {self.permission_name}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name'], name='jobperm_name_unique')
        ]


class JobPermissionMapping(BareModel):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    permission = models.ForeignKey(JobPermission, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"Permission '{self.permission.name}' linked to job '{self.job.name}'"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['job', 'permission'], name='jobpermmap_unique')
        ]


class JobCredentialsPermissionMapping(BareModel):
    credentials = models.ForeignKey(JobGlobalCredentials, on_delete=models.CASCADE)
    permission = models.ForeignKey(JobPermission, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"Permission '{self.permission.name}' linked to credentials '{self.credentials.name}'"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['credentials', 'permission'], name='jobcredpermmap_unique')
        ]


class JobRepositoryPermissionMapping(BareModel):
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE)
    permission = models.ForeignKey(JobPermission, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"Permission '{self.permission.name}' linked to repository '{self.repository.name}'"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['repository', 'permission'], name='jobrepopermmap_unique')
        ]


class JobPermissionMemberUser(BareModel):
    user = models.ForeignKey(USERS, on_delete=models.CASCADE)
    permission = models.ForeignKey(JobPermission, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"Permission '{self.permission.name}' member user '{self.user.username}'"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'permission'], name='jobpermmemberuser_unique')
        ]


class JobPermissionMemberGroup(BareModel):
    group = models.ForeignKey(GROUPS, on_delete=models.CASCADE)
    permission = models.ForeignKey(JobPermission, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"Permission '{self.permission.name}' member group '{self.group.name}'"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['group', 'permission'], name='jobpermmembergrp_unique')
        ]
