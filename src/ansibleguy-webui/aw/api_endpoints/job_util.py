from pathlib import Path

from django.shortcuts import HttpResponse
from rest_framework import serializers

from aw.config.main import config
from aw.config.hardcoded import JOB_EXECUTION_LIMIT
from aw.model.job import Job, JobExecution
from aw.utils.permission import get_viewable_jobs
from aw.utils.util import get_next_cron_execution_str
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
    log_stderr_repo_url = serializers.CharField(required=False)
    log_stdout_repo = serializers.CharField(required=False)
    log_stdout_repo_url = serializers.CharField(required=False)
    log_stderr_repo = serializers.CharField(required=False)


def get_job_execution_serialized(execution: JobExecution) -> dict:
    serialized = JobExecutionReadResponse(instance=execution).data
    serialized['job'] = execution.job.id
    serialized['job_name'] = execution.job.name
    serialized['job_comment'] = execution.job.comment
    serialized['user'] = execution.user.id if execution.user is not None else None
    serialized['user_name'] = execution.user.username if execution.user is not None else 'Scheduled'
    serialized['time_start'] = execution.time_created_str
    serialized['time_fin'] = None
    serialized['failed'] = None
    serialized['error_s'] = None
    serialized['error_m'] = None

    for logfile in JobExecution.log_file_fields:
        if serialized[logfile] is None or not Path(serialized[logfile]).is_file():
            serialized[logfile] = None
            serialized[logfile + '_url'] = None

    if execution.result is not None:
        serialized['time_fin'] = execution.result.time_fin_str
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
            if job.schedule is not None and job.enabled:
                job_serialized['next_run'] = get_next_cron_execution_str(job.schedule) + f" {config['timezone']}"

        except ValueError:
            pass

        if executions:
            job_serialized['executions'] = get_job_executions_serialized(job=job, execution_count=execution_count)

        serialized.append(job_serialized)

    return serialized


def get_log_file_content(logfile: (str, Path)) -> HttpResponse:
    with open(logfile, 'rb') as _logfile:
        content_b = _logfile.read()
        if content_b == b'':
            return HttpResponse(content_b, content_type='text/plain', status=404)

        response = HttpResponse(content_b, content_type='text/plain', status=200)

    response['Content-Disposition'] = f"inline; filename={logfile.rsplit('/', 1)[1]}"
    return response
