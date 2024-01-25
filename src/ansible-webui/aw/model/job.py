from crontab import CronTab
from django.db import models
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.validators import ValidationError
from django.utils import timezone

from aw.model.base import BareModel, BaseModel, CHOICES_BOOL, DEFAULT_NONE
from aw.config.hardcoded import SHORT_TIME_FORMAT
from aw.utils.util import is_null
from aw.utils.crypto import encrypt, decrypt


class JobError(BareModel):
    short = models.CharField(max_length=100)
    med = models.TextField(max_length=1024, null=True)
    logfile = models.CharField(max_length=300, **DEFAULT_NONE)

    def __str__(self) -> str:
        return f"Job error {self.created}: '{self.short}'"


CHOICES_JOB_VERBOSITY = (
    (0, 'Default'),
    (1, 'v'),
    (2, 'vv'),
    (3, 'vvv'),
    (4, 'vvvv'),
    (5, 'vvvv'),
    (6, 'vvvvvv'),
)


class BaseJobCredentials(BaseModel):
    connect_user = models.CharField(max_length=100, **DEFAULT_NONE)
    become_user = models.CharField(max_length=100, **DEFAULT_NONE)
    vault_file = models.CharField(max_length=300, **DEFAULT_NONE)
    vault_id = models.CharField(max_length=50, **DEFAULT_NONE)

    _enc_vault_pass = models.CharField(max_length=500, **DEFAULT_NONE)
    _enc_become_pass = models.CharField(max_length=500, **DEFAULT_NONE)
    _enc_connect_pass = models.CharField(max_length=500, **DEFAULT_NONE)

    @property
    def vault_pass(self) -> str:
        if is_null(self._enc_vault_pass):
            return ''

        return decrypt(self._enc_vault_pass)

    @vault_pass.setter
    def vault_pass(self, value: str):
        if is_null(value):
            self._enc_vault_pass = None

        self._enc_vault_pass = encrypt(value)

    @property
    def become_pass(self) -> str:
        if is_null(self._enc_become_pass):
            return ''

        return decrypt(self._enc_become_pass)

    @become_pass.setter
    def become_pass(self, value: str):
        if is_null(value):
            self._enc_become_pass = None

        self._enc_become_pass = encrypt(value)

    @property
    def connect_pass(self) -> str:
        if is_null(self._enc_connect_pass):
            return ''

        return decrypt(self._enc_connect_pass)

    @connect_pass.setter
    def connect_pass(self, value: str):
        if is_null(value):
            self._enc_connect_pass = None

        self._enc_connect_pass = encrypt(value)

    class Meta:
        abstract = True


class JobUserCredentials(BaseJobCredentials):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        # pylint: disable=E1101
        return f"Credentials '{self.name}' of user '{self.user.username}'"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'name'], name='jobusercreds_user_name')
        ]


class BaseJob(BaseJobCredentials):
    BAD_ANSIBLE_FLAGS = [
        'step', 'ask-vault-password', 'ask-vault-pass', 'k', 'ask-pass',
    ]

    limit = models.CharField(max_length=500, **DEFAULT_NONE)
    verbosity = models.PositiveSmallIntegerField(choices=CHOICES_JOB_VERBOSITY, default=0)
    comment = models.CharField(max_length=150, **DEFAULT_NONE)
    mode_diff = models.BooleanField(choices=CHOICES_BOOL, default=False)
    mode_check = models.BooleanField(choices=CHOICES_BOOL, default=False)

    # NOTE: one or multiple comma-separated vars
    environment_vars = models.CharField(max_length=1000, **DEFAULT_NONE)

    tags = models.CharField(max_length=150, **DEFAULT_NONE)
    tags_skip = models.CharField(max_length=150, **DEFAULT_NONE)
    cmd_args = models.CharField(max_length=150, **DEFAULT_NONE)

    class Meta:
        abstract = True

    def clean(self):
        # pylint: disable=E1101
        super().clean()

        for flag in self.BAD_ANSIBLE_FLAGS:
            for search in [f'-{flag} ', f'-{flag}=', f'-{flag}']:
                if self.cmd_args.find(search) != -1:
                    raise ValidationError(
                        f"Found one or more bad flags in commandline arguments: {self.BAD_ANSIBLE_FLAGS} (prompts)"
                    )


def validate_cronjob(value):
    try:
        _ = CronTab(value)
        return value

    except ValueError:
        raise ValidationError('The provided schedule is not in a valid cron format')


class Job(BaseJob):
    CHANGE_FIELDS = [
        'name', 'inventory', 'playbook', 'schedule', 'limit', 'verbosity', 'environment_vars', 'mode_diff',
        'mode_check', 'tags', 'tags_skip', 'verbosity', 'comment', 'environment_vars', 'connect_user', 'become_user',
        'cmd_args', 'vault_id', 'vault_file', 'enabled',
    ]
    form_fields = CHANGE_FIELDS
    api_fields = ['id']
    api_fields.extend(CHANGE_FIELDS)

    name = models.CharField(max_length=150)
    inventory = models.CharField(max_length=300)  # NOTE: one or multiple comma-separated inventories
    playbook = models.CharField(max_length=100)
    schedule_max_len = 50
    schedule = models.CharField(max_length=schedule_max_len, validators=[validate_cronjob], blank=True, default=None)
    enabled = models.BooleanField(choices=CHOICES_BOOL, default=True)

    def __str__(self) -> str:
        limit = '' if self.limit is None else f' [{self.limit}]'
        return f"Job '{self.name}' ({self.playbook} => {self.inventory}{limit})"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name'], name='job_name_unique')
        ]


CHOICE_JOB_PERMISSION_READ = 5
CHOICE_JOB_PERMISSION_EXECUTE = 10
CHOICE_JOB_PERMISSION_WRITE = 15
CHOICE_JOB_PERMISSION_FULL = 20
CHOICES_JOB_PERMISSION = (
    (0, 'None'),
    (CHOICE_JOB_PERMISSION_READ, 'Read'),
    (CHOICE_JOB_PERMISSION_EXECUTE, 'Execute'),
    (CHOICE_JOB_PERMISSION_WRITE, 'Write'),
    (CHOICE_JOB_PERMISSION_FULL, 'Full'),
)


class JobPermission(BaseModel):
    name = models.CharField(max_length=100)
    permission = models.PositiveSmallIntegerField(choices=CHOICES_JOB_PERMISSION, default=0)
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='JobPermissionMemberUser',
        through_fields=('permission', 'user'),
    )
    groups = models.ManyToManyField(
        Group,
        through='JobPermissionMemberGroup',
        through_fields=('permission', 'group'),
    )

    def __str__(self) -> str:
        return f"Permission '{self.name}' - {self.permission}"

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


class JobPermissionMemberUser(BareModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    permission = models.ForeignKey(JobPermission, on_delete=models.CASCADE)

    def __str__(self) -> str:
        # pylint: disable=E1101
        return f"Permission '{self.permission.name}' member user '{self.user.username}'"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'permission'], name='jobpermmemberuser_unique')
        ]


class JobPermissionMemberGroup(BareModel):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    permission = models.ForeignKey(JobPermission, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"Permission '{self.permission.name}' member group '{self.group.name}'"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['group', 'permission'], name='jobpermmembergrp_unique')
        ]


class JobExecutionResult(BareModel):
    # ansible_runner.runner.Runner
    time_start = models.DateTimeField(default=timezone.now)
    time_fin = models.DateTimeField(**DEFAULT_NONE)

    failed = models.BooleanField(choices=CHOICES_BOOL, default=False)
    error = models.ForeignKey(JobError, on_delete=models.SET_NULL, related_name='jobresult_fk_error', null=True)

    def __str__(self) -> str:
        result = 'succeeded'

        if self.failed:
            result = 'failed'

        return f"Job execution {self.time_start}: {result}"


class JobExecutionResultHost(BareModel):
    STATS = [
        'unreachable', 'tasks_skipped', 'tasks_ok', 'tasks_failed', 'tasks_rescued',
        'tasks_ignored', 'tasks_changed',
    ]
    # ansible_runner.runner.Runner.stats
    hostname = models.CharField(max_length=300, null=False)
    unreachable = models.BooleanField(choices=CHOICES_BOOL, default=False)

    tasks_skipped = models.PositiveSmallIntegerField(default=0)
    tasks_ok = models.PositiveSmallIntegerField(default=0)
    tasks_failed = models.PositiveSmallIntegerField(default=0)
    tasks_rescued = models.PositiveSmallIntegerField(default=0)
    tasks_ignored = models.PositiveSmallIntegerField(default=0)
    tasks_changed = models.PositiveSmallIntegerField(default=0)

    error = models.ForeignKey(JobError, on_delete=models.SET_NULL, related_name='jobresulthost_fk_error', null=True)
    result = models.ForeignKey(
        JobExecutionResult, on_delete=models.CASCADE, related_name='jobresulthost_fk_result', null=True
    )

    def __str__(self) -> str:
        result = 'succeeded'

        if int(self.tasks_failed) > 0:
            result = 'failed'

        return f"Job execution {self.created} of host '{self.hostname}': {result}"


CHOICES_JOB_EXEC_STATUS = [
    (0, 'Waiting'),
    (1, 'Starting'),
    (2, 'Running'),
    (3, 'Failed'),
    (4, 'Finished'),
]


class JobExecution(BaseJob):
    # NOTE: scheduled execution will have no user
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        related_name='jobexec_fk_user', editable=False,
    )
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='jobexec_fk_job')
    result = models.ForeignKey(
        JobExecutionResult, on_delete=models.SET_NULL, related_name='jobexec_fk_result',
        **DEFAULT_NONE,  # execution is created before result is available
    )
    status = models.PositiveSmallIntegerField(default=0, choices=CHOICES_JOB_EXEC_STATUS)
    user_credentials = models.ForeignKey(
        Job, on_delete=models.SET_NULL, related_name='jobexec_fk_usercreds', **DEFAULT_NONE,
    )

    def __str__(self) -> str:
        # pylint: disable=E1101
        status_name = CHOICES_JOB_EXEC_STATUS[int(self.status)][1]
        executor = 'scheduled'
        if self.user is not None:
            executor = self.user.username

        timestamp = self.created.strftime(SHORT_TIME_FORMAT)
        return f"Job '{self.job.name}' execution @ {timestamp} by '{executor}': {status_name}"


class JobQueue(BareModel):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='jobqueue_fk_job')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        related_name='jobqueue_fk_user',
    )
