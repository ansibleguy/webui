from django.db import models
from django.conf import settings
from django.contrib.auth.models import Group

from crontab import CronTab

from aw.model.base import BareModel, BaseModel, CHOICES_BOOL


class JobError(BareModel):
    short = models.CharField(max_length=100)
    med = models.TextField(max_length=1024, null=True)
    logfile = models.FilePathField()

    def __str__(self) -> str:
        return f"Job error {self.created}: '{self.short}'"


class JobPermission(BaseModel):
    name = models.CharField(max_length=100)
    permission = models.CharField(
        max_length=50,
        choices=[('full', 'Full'), ('read', 'Read'), ('write', 'Write'), ('execute', 'Execute')],
    )
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


class JobPermissionMemberUser(BareModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    permission = models.ForeignKey(JobPermission, on_delete=models.CASCADE)


class JobPermissionMemberGroup(BareModel):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    permission = models.ForeignKey(JobPermission, on_delete=models.CASCADE)


CHOICES_JOB_VERBOSITY = (
    (0, 'None'),
    (1, 'v'),
    (2, 'vv'),
    (3, 'vvv'),
    (4, 'vvvv'),
    (5, 'vvvv'),
    (6, 'vvvvvv'),
)


class MetaJob(BaseModel):
    limit = models.CharField(max_length=500, null=True, default=None)
    verbosity = models.PositiveSmallIntegerField(choices=CHOICES_JOB_VERBOSITY, default=0)

    # NOTE: one or multiple comma-separated vars
    environment_vars = models.CharField(max_length=1000, null=True, default=None)

    class Meta:
        abstract = True


class Job(MetaJob):
    job_id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=150)
    inventory = models.CharField(max_length=300)  # NOTE: one or multiple comma-separated inventories
    playbook = models.CharField(max_length=300)  # NOTE: one or multiple comma-separated playbooks
    schedule = models.CharField(max_length=50, validators=[CronTab])
    permission = models.ForeignKey(JobPermission, on_delete=models.SET_NULL, null=True)

    def __str__(self) -> str:
        return f"Job '{self.name}' ('{self.playbook}')"


class JobExecutionResult(BareModel):
    # ansible_runner.runner.Runner
    time_start = models.DateTimeField(auto_now_add=True)
    time_fin = models.DateTimeField(blank=True, null=True, default=None)

    failed = models.BooleanField(choices=CHOICES_BOOL, default=False)


class JobExecutionResultHost(BareModel):
    # ansible_runner.runner.Runner.stats
    hostname = models.CharField(max_length=300)
    unreachable = models.BooleanField(choices=CHOICES_BOOL, default=False)

    tasks_skipped = models.PositiveSmallIntegerField(default=0)
    tasks_ok = models.PositiveSmallIntegerField(default=0)
    tasks_failed = models.PositiveSmallIntegerField(default=0)
    tasks_rescued = models.PositiveSmallIntegerField(default=0)
    tasks_ignored = models.PositiveSmallIntegerField(default=0)
    tasks_changed = models.PositiveSmallIntegerField(default=0)

    error = models.ForeignKey(JobError, on_delete=models.CASCADE, related_name='jobresulthost_fk_error')
    result = models.ForeignKey(JobExecutionResult, on_delete=models.CASCADE, related_name='jobresulthost_fk_result')

    def __str__(self) -> str:
        result = 'succeeded'

        if int(self.tasks_failed) > 0:
            result = 'failed'

        return f"Job execution {self.created} of host {self.hostname}: {result}"


CHOICES_JOB_EXEC_STATUS = [
    (0, 'Waiting'),
    (1, 'Starting'),
    (2, 'Running'),
    (3, 'Failed'),
    (4, 'Finished'),
]


class JobExecution(MetaJob):
    # NOTE: scheduled execution will have no user
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True,
        related_name='jobexec_fk_user'
    )
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='jobexec_fk_job')
    result = models.ForeignKey(
        JobExecutionResult, on_delete=models.CASCADE, related_name='jobexec_fk_result',
        null=True, default=None,  # execution is created before result is available
    )
    status = models.PositiveSmallIntegerField(default=0, choices=CHOICES_JOB_EXEC_STATUS)
    comment = models.CharField(max_length=300, null=True, default=None)

    def __str__(self) -> str:
        status_name = CHOICES_JOB_EXEC_STATUS[int(self.status)][1]
        return f"Job '{self.job.name}' execution {self.created}: {status_name}"
