from django.shortcuts import redirect, render
from django.shortcuts import HttpResponse
from django.urls import path
from django.forms import ModelForm

from aw.utils.http import ui_endpoint_wrapper
from aw.model.job import Job, JobExecution, CHOICES_JOB_EXEC_STATUS
from aw.api_endpoints.job_util import get_viewable_jobs
from aw.config.form_metadata import FORM_LABEL, FORM_HELP


@ui_endpoint_wrapper
def manage(request) -> HttpResponse:
    jobs_viewable = get_viewable_jobs(request.user)
    executions = {}

    for job in jobs_viewable:
        # pylint: disable=E1101
        executions[job.id] = JobExecution.objects.filter(job=job).order_by('-updated')

    return render(
        request, status=200, template_name='jobs/manage.html',
        context={'jobs': jobs_viewable, 'executions': executions, 'execution_stati': CHOICES_JOB_EXEC_STATUS}
    )


class JobForm(ModelForm):
    class Meta:
        model = Job
        fields = Job.form_fields
        labels = FORM_LABEL['jobs']['manage']['job']
        help_texts = FORM_HELP['jobs']['manage']['job']


@ui_endpoint_wrapper
def job_edit(request, job_id: int = None) -> HttpResponse:
    job_form = JobForm()
    job_form_html = job_form.render(template_name='forms/snippet.html')
    form_method = 'post'
    form_api = 'job'

    if job_id is not None:
        # pylint: disable=E1101
        result = Job.objects.filter(id=job_id)
        if not result.exists():
            return redirect('ui/jobs/manage')

        job_form.instance = result
        form_method = 'put'
        form_api += f'/{job_id}'

    return render(
        request, status=200, template_name='jobs/edit.html',
        context={'form': job_form_html, 'form_api': form_api, 'form_method': form_method}
    )


urlpatterns_jobs = [
    path('ui/jobs/manage', manage),
    path('ui/jobs/manage/job', job_edit),
    path('ui/jobs/manage/job/<int:job_id>', job_edit),
]
