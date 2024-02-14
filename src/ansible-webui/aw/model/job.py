from crontab import CronTab
from django.db import models
from django.core.validators import ValidationError
from django.utils import timezone

from aw.model.base import BareModel, BaseModel, CHOICES_BOOL, DEFAULT_NONE
from aw.config.hardcoded import SHORT_TIME_FORMAT
from aw.model.job_credential import JobGlobalCredentials, JobUserCredentials
from aw.base import USERS


class JobError(BareModel):
    short = models.CharField(max_length=100)
    med = models.TextField(max_length=1024, null=True)

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


class BaseJob(BaseModel):
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
        'name', 'inventory_file', 'playbook_file', 'schedule', 'enabled', 'limit', 'verbosity', 'mode_diff',
        'mode_check', 'tags', 'tags_skip', 'verbosity', 'comment', 'environment_vars', 'cmd_args',
        'credentials_default', 'credentials_needed',
    ]
    form_fields = CHANGE_FIELDS
    api_fields_read = ['id']
    api_fields_read.extend(CHANGE_FIELDS)
    api_fields_write = api_fields_read.copy()
    api_fields_read.append('next_run')

    name = models.CharField(max_length=150)
    inventory_file = models.CharField(max_length=300)  # NOTE: one or multiple comma-separated inventories
    playbook_file = models.CharField(max_length=100)
    schedule_max_len = 50
    schedule = models.CharField(max_length=schedule_max_len, validators=[validate_cronjob], **DEFAULT_NONE)
    enabled = models.BooleanField(choices=CHOICES_BOOL, default=True)

    credentials_needed = models.BooleanField(choices=CHOICES_BOOL, default=True)
    credentials_default = models.ForeignKey(
        JobGlobalCredentials, on_delete=models.SET_NULL, related_name='job_fk_creddflt', null=True, blank=True,
    )

    def __str__(self) -> str:
        limit = '' if self.limit is None else f' [{self.limit}]'
        return f"Job '{self.name}' ({self.playbook_file} => {self.inventory_file}{limit})"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name'], name='job_name_unique')
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
    (5, 'Stopping'),
    (6, 'Stopped'),
]


class JobExecution(BaseJob):
    api_fields_read = [
        'id', 'job', 'job_name', 'user', 'user_name', 'result', 'status', 'status_name', 'time_start', 'time_fin',
        'failed', 'error_s', 'error_m', 'log_stdout', 'log_stdout_url', 'log_stderr', 'log_stderr_url', 'job_comment',
        'credential_global', 'credential_user',
    ]

    # NOTE: scheduled execution will have no user
    user = models.ForeignKey(
        USERS, on_delete=models.SET_NULL, null=True,
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
    log_stdout = models.CharField(max_length=300, **DEFAULT_NONE)
    log_stderr = models.CharField(max_length=300, **DEFAULT_NONE)
    command = models.CharField(max_length=1000, **DEFAULT_NONE)

    credential_global = models.ForeignKey(
        JobGlobalCredentials, on_delete=models.SET_NULL, related_name='jobexec_fk_credglob', null=True,
    )
    credential_user = models.ForeignKey(
        JobUserCredentials, on_delete=models.SET_NULL, related_name='jobexec_fk_credusr', null=True,
    )

    def __str__(self) -> str:
        status_name = CHOICES_JOB_EXEC_STATUS[int(self.status)][1]
        executor = 'scheduled'
        if self.user is not None:
            executor = self.user.username

        timestamp = self.created.strftime(SHORT_TIME_FORMAT)
        return f"Job '{self.job.name}' execution @ {timestamp} by '{executor}': {status_name}"


class JobQueue(BareModel):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='jobqueue_fk_job')
    user = models.ForeignKey(
        USERS, on_delete=models.SET_NULL, null=True,
        related_name='jobqueue_fk_user',
    )
