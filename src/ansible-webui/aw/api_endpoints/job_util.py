from rest_framework import serializers

from aw.config.hardcoded import SHORT_TIME_FORMAT, JOB_EXECUTION_LIMIT
from aw.model.job import Job, CHOICES_JOB_EXEC_STATUS, JobExecution
from aw.utils.permission import get_viewable_jobs
from aw.utils.util import datetime_from_db, get_next_cron_execution_str
from aw.base import USERS


class JobReadResponse(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = Job.api_fields_read

    next_run = serializers.CharField(required=False)


class JobExecutionReadResponse(serializers.ModelSerializer):
    class Meta:
        model = JobExecution
        fields = JobExecution.api_fields_read

    job_name = serializers.CharField(required=False)
    job_comment = serializers.CharField(required=False)
    user_name = serializers.CharField(required=False)
    status_name = serializers.CharField(required=False)
    failed = serializers.BooleanField(required=False)
    error_s = serializers.CharField(required=False)
    error_m = serializers.CharField(required=False)
    time_start = serializers.CharField(required=False)
    time_fin = serializers.CharField(required=False)
    log_stdout = serializers.CharField(required=False)
    log_stdout_url = serializers.CharField(required=False)
    log_stderr = serializers.CharField(required=False)
    log_stderr_url = serializers.CharField(required=False)


def get_job_execution_serialized(execution: JobExecution) -> dict:
    serialized = {
        'id': execution.id,
        'job': execution.job.id,
        'job_name': execution.job.name,
        'job_comment': execution.job.comment,
        'user': execution.user.id if execution.user is not None else None,
        'user_name': execution.user.username if execution.user is not None else 'Scheduled',
        'command': execution.command,
        'status': execution.status,
        'status_name': CHOICES_JOB_EXEC_STATUS[execution.status][1],
        'time_start': datetime_from_db(execution.created).strftime(SHORT_TIME_FORMAT),
        'time_fin': None,
        'failed': None,
        'error_s': None,
        'error_m': None,
        'log_stdout': execution.log_stdout,
        'log_stdout_url': f"/api/job/{execution.job.id}/{execution.id}/log",
        'log_stderr': execution.log_stderr,
        'log_stderr_url': f"/api/job/{execution.job.id}/{execution.id}/log?type=stderr",
    }
    if execution.result is not None:
        serialized['time_fin'] = datetime_from_db(execution.result.time_fin).strftime(SHORT_TIME_FORMAT)
        serialized['failed'] = execution.result.failed
        if execution.result.error is not None:
            serialized['error_s'] = execution.result.error.short
            serialized['error_m'] = execution.result.error.med

    return serialized


def get_job_executions_serialized(job: Job, execution_count: int = JOB_EXECUTION_LIMIT) -> list[dict]:
    serialized = []
    for execution in JobExecution.objects.filter(job=job).order_by('-updated')[:execution_count]:
        serialized.append(get_job_execution_serialized(execution))

    return serialized


def get_viewable_jobs_serialized(
        user: USERS, executions: bool = False,
        execution_count: int = None
) -> list[dict]:
    serialized = []

    for job in get_viewable_jobs(user):
        job_serialized = JobReadResponse(instance=job).data
        job_serialized['next_run'] = None

        try:
            if job.schedule is not None:
                job_serialized['next_run'] = get_next_cron_execution_str(job.schedule)

        except ValueError:
            pass

        if executions:
            job_serialized['executions'] = get_job_executions_serialized(job=job, execution_count=execution_count)

        serialized.append(job_serialized)

    return serialized
