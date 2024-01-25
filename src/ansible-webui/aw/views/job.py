from django.shortcuts import redirect, render
from django.shortcuts import HttpResponse
from django.urls import path
from django.forms import ModelForm, CharField, PasswordInput
from django.core.validators import RegexValidator

from aw.utils.http import ui_endpoint_wrapper, ui_endpoint_wrapper_kwargs
from aw.model.job import Job, JobExecution, CHOICE_JOB_PERMISSION_WRITE, JobExecutionResultHost
from aw.api_endpoints.job_util import get_viewable_jobs, job_action_allowed
from aw.config.form_metadata import FORM_LABEL, FORM_HELP
from aw.utils.util import get_next_cron_execution_str

LIMIT_JOB_RESULTS = 10


@ui_endpoint_wrapper
def manage(request) -> HttpResponse:
    jobs_viewable = get_viewable_jobs(request.user)
    executions = {}
    next_executions = {}
    execution_results_hosts = {}

    for job in jobs_viewable:
        # pylint: disable=E1101
        executions[job.id] = JobExecution.objects.filter(job=job).order_by('-updated')[:LIMIT_JOB_RESULTS]

        try:
            cron = get_next_cron_execution_str(job.schedule)

        except ValueError:
            cron = '-'

        next_executions[job.id] = cron

        for execution in executions[job.id]:
            if execution.result is not None:
                execution_results_hosts[execution.id] = JobExecutionResultHost.objects.filter(
                    result=execution.result,
                ).order_by('-created')

    return render(
        request, status=200, template_name='jobs/manage.html',
        context={
            'jobs': jobs_viewable, 'executions': executions, 'next_executions': next_executions,
            'show_update_time': True, 'execution_results_hosts': execution_results_hosts,
        }
    )


class JobForm(ModelForm):
    class Meta:
        model = Job
        fields = Job.form_fields
        field_order = Job.form_fields
        labels = FORM_LABEL['jobs']['manage']['job']
        help_texts = FORM_HELP['jobs']['manage']['job']

    vault_pass = CharField(widget=PasswordInput(), max_length=100, required=False)
    become_pass = CharField(widget=PasswordInput(), max_length=100, required=False)
    connect_pass = CharField(widget=PasswordInput(), max_length=100, required=False)

    # form not picking up regex-validator
    schedule = CharField(
        max_length=Job.schedule_max_len,
        validators=[RegexValidator(
            regex=r'^(@(annually|yearly|monthly|weekly|daily|hourly))|'
                  r'(@every (\d+(s|m|h))+)|'
                  r'((((\d+,)+\d+|(\d+(\/|-|#)\d+)|\d+L?|\*(\/\d+)?|L(-\d+)?|\?|[A-Z]{3}(-[A-Z]{3})?) ?){5,7})$',
            message='The provided schedule is not in a valid cron format',
        )],
        required=False,
        help_text=Meta.help_texts['schedule'],
    )


@ui_endpoint_wrapper_kwargs
def job_edit(request, job_id: int = None) -> HttpResponse:
    job_form = JobForm()
    form_method = 'post'
    form_api = 'job'
    job = {}

    if job_id is not None:
        # pylint: disable=E1101
        job = Job.objects.filter(id=job_id).first()
        if job is None:
            return redirect(f"/ui/jobs/manage?error=Job with ID {job_id} does not exist")

        if not job_action_allowed(user=request.user, job=job, permission_needed=CHOICE_JOB_PERMISSION_WRITE):
            return redirect(f"/ui/jobs/manage?error=Not privileged to modify the job '{job.name}'")

        job = job.__dict__
        form_method = 'put'
        form_api += f'/{job_id}'

    job_form_html = job_form.render(
        template_name='forms/snippet.html',
        context={'form': job_form, 'existing': job},
    )
    # job_form_html = job_form.render(template_name='forms/snippet.html', context={'existing': job})
    return render(
        request, status=200, template_name='jobs/edit.html',
        context={'form': job_form_html, 'form_api': form_api, 'form_method': form_method}
    )


urlpatterns_jobs = [
    path('ui/jobs/manage/job/<int:job_id>', job_edit),
    path('ui/jobs/manage/job', job_edit),
    path('ui/jobs/manage', manage),
]
