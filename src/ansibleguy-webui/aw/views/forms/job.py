from django import forms
from django.shortcuts import redirect, render
from django.shortcuts import HttpResponse
from django.core.validators import RegexValidator
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

from aw.config.main import config
from aw.utils.http import ui_endpoint_wrapper_kwargs
from aw.model.job import Job
from aw.model.permission import CHOICE_PERMISSION_WRITE
from aw.model.job_credential import JobGlobalCredentials, JobUserCredentials
from aw.model.repository import Repository
from aw.api_endpoints.credentials import are_global_credentials
from aw.utils.permission import has_job_permission, has_credentials_permission
from aw.config.form_metadata import FORM_LABEL, FORM_HELP
from aw.views.base import choices_global_credentials, choices_repositories


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = Job.form_fields
        field_order = Job.form_fields
        labels = FORM_LABEL['jobs']['manage']
        help_texts = FORM_HELP['jobs']['manage']

    credentials_default = forms.ChoiceField(
        required=False,
        widget=forms.Select,
        choices=choices_global_credentials,
        label=FORM_LABEL['jobs']['manage']['credentials_default'],
    )

    repository = forms.ChoiceField(
        required=False,
        widget=forms.Select,
        choices=choices_repositories,
        label=FORM_LABEL['jobs']['manage']['repository'],
    )

    # form not picking up regex-validator
    schedule = forms.CharField(
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


@login_required
@ui_endpoint_wrapper_kwargs
def job_edit(request, job_id: int = None) -> HttpResponse:
    job_form = JobForm()
    form_method = 'post'
    form_api = 'job'
    job = {}

    if job_id is not None:
        try:
            job = Job.objects.get(id=job_id)

        except ObjectDoesNotExist:
            job = None

        if job is None:
            return redirect(f"/ui/jobs/manage?error=Job with ID {job_id} does not exist")

        if not has_job_permission(user=request.user, job=job, permission_needed=CHOICE_PERMISSION_WRITE):
            return redirect(f"/ui/jobs/manage?error=Not privileged to modify the job '{job.name}'")

        job = job.__dict__
        form_method = 'put'
        form_api += f'/{job_id}'

    job_form_html = job_form.render(
        template_name='forms/job.html',
        context={'form': job_form, 'existing': job, 'primary_fields': Job.form_fields_primary},
    )
    return render(
        request, status=200, template_name='jobs/edit.html',
        context={'form': job_form_html, 'form_api': form_api, 'form_method': form_method}
    )


class CredentialGlobalForm(forms.ModelForm):
    class Meta:
        model = JobGlobalCredentials
        fields = JobGlobalCredentials.form_fields
        field_order = JobGlobalCredentials.form_fields
        labels = FORM_LABEL['jobs']['credentials']
        help_texts = FORM_HELP['jobs']['credentials']

    vault_pass = forms.CharField(
        max_length=100, required=False, label=FORM_LABEL['jobs']['credentials']['vault_pass'],
    )
    become_pass = forms.CharField(
        max_length=100, required=False, label=FORM_LABEL['jobs']['credentials']['become_pass'],
    )
    connect_pass = forms.CharField(
        max_length=100, required=False, label=FORM_LABEL['jobs']['credentials']['connect_pass'],
    )
    ssh_key = forms.CharField(
        max_length=2000, required=False, label=FORM_LABEL['jobs']['credentials']['ssh_key'],
    )


class CredentialUserForm(CredentialGlobalForm):
    class Meta:
        model = JobUserCredentials
        fields = JobUserCredentials.form_fields
        field_order = JobUserCredentials.form_fields


@login_required
@ui_endpoint_wrapper_kwargs
def job_credentials_edit(request, credentials_id: int = None) -> HttpResponse:
    are_global = are_global_credentials(request)
    if are_global:
        credentials_form = CredentialGlobalForm()
    else:
        credentials_form = CredentialUserForm()

    form_method = 'post'
    form_api = 'credentials'
    credentials = {}

    if credentials_id is not None and credentials_id != 0:
        try:
            if are_global:
                credentials = JobGlobalCredentials.objects.get(id=credentials_id)

            else:
                credentials = JobUserCredentials.objects.get(id=credentials_id, user=request.user)

        except ObjectDoesNotExist:
            credentials = None

        if credentials is None:
            return redirect(f"/ui/jobs/credentials?error=Credentials with ID {credentials_id} do not exist")

        if isinstance(credentials, JobGlobalCredentials) and not has_credentials_permission(
                user=request.user,
                credentials=credentials,
                permission_needed=CHOICE_PERMISSION_WRITE,
        ):
            return redirect(
                f"/ui/jobs/credentials?error=Not privileged to modify the credentials '{credentials.name}'",
            )

        credentials = credentials.__dict__
        form_method = 'put'
        form_api += f'/{credentials_id}'

    form_api += '?global=true' if are_global else '?global=false'
    credentials_form_html = credentials_form.render(
        template_name='forms/snippet.html',
        context={'form': credentials_form, 'existing': credentials},
    )
    return render(
        request, status=200, template_name='jobs/credentials_edit.html',
        context={'form': credentials_form_html, 'form_api': form_api, 'form_method': form_method}
    )


class RepositoryForm(forms.ModelForm):
    class Meta:
        model = Repository
        fields = Repository.form_fields
        field_order = Repository.form_fields
        labels = FORM_LABEL['jobs']['repository']
        help_texts = FORM_HELP['jobs']['repository']

    static_path = forms.CharField(max_length=500, initial=config['path_play'], required=False)

    git_credentials = forms.ChoiceField(
        required=False,
        widget=forms.Select,
        choices=choices_global_credentials,
        label=FORM_LABEL['jobs']['repository']['git_credentials'],
    )


@login_required
@ui_endpoint_wrapper_kwargs
def job_repository_edit(request, repo_id: int = None) -> HttpResponse:
    form_method = 'post'
    form_api = 'repository'
    repository = {}

    if repo_id is not None and repo_id != 0:
        # pylint: disable=R0801
        try:
            repository = Repository.objects.get(id=repo_id)

        except ObjectDoesNotExist:
            repository = None

        if repository is None:
            return redirect(f"/ui/jobs/repository?error=Repository with ID {repo_id} do not exist")

        repository = repository.__dict__
        form_method = 'put'
        form_api += f'/{repo_id}'

    repository_form = RepositoryForm()
    repository_form_html = repository_form.render(
        template_name='forms/snippet.html',
        context={'form': repository_form, 'existing': repository},
    )
    return render(
        request, status=200, template_name='jobs/repository_edit.html',
        context={'form': repository_form_html, 'form_api': form_api, 'form_method': form_method}
    )
