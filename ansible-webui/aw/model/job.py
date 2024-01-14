from django.db import models
from django.conf import settings

from crontab import CronTab

from aw.model.base import BareModel


class JobError(BareModel):
    field_list = ['short', 'logfile']

    short = models.TextField(max_length=1024)
    logfile = models.FilePathField()


class Job(BareModel):
    field_list = ['inventory', 'playbook', 'schedule', 'name', 'job_id']

    inventory = models.CharField(max_length=150)
    playbook = models.CharField(max_length=150)
    schedule = models.CharField(max_length=50, validators=[CronTab])
    name = models.CharField(max_length=100)
    job_id = models.PositiveIntegerField(max_length=50)


class JobExecution(BareModel):
    field_list = [
        'user', 'start', 'fin', 'error',
        'result_ok', 'result_changed', 'result_unreachable', 'result_failed', 'result_skipped',
        'result_rescued', 'result_ignored',
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, blank=True, null=True,
        related_name=f"jobexec_fk_user"
    )
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name=f"jobexec_fk_job")
    start = models.DateTimeField(auto_now_add=True)
    fin = models.DateTimeField(blank=True, null=True, default=None)
    error = models.ForeignKey(JobError, on_delete=models.CASCADE, related_name=f"jobexec_fk_error")
    result_ok = models.PositiveSmallIntegerField(default=0)
    result_changed = models.PositiveSmallIntegerField(default=0)
    result_unreachable = models.PositiveSmallIntegerField(default=0)
    result_failed = models.PositiveSmallIntegerField(default=0)
    result_skipped = models.PositiveSmallIntegerField(default=0)
    result_rescued = models.PositiveSmallIntegerField(default=0)
    result_ignored = models.PositiveSmallIntegerField(default=0)
