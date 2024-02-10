from django.urls import path
from django.contrib.auth.models import User, Group
from django.shortcuts import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.forms import ModelForm, SelectMultiple, MultipleChoiceField

from aw.utils.http import ui_endpoint_wrapper, ui_endpoint_wrapper_kwargs
from aw.model.job import Job, JobPermission
from aw.config.form_metadata import FORM_LABEL, FORM_HELP


@login_required
@ui_endpoint_wrapper
def setting_api_key(request) -> HttpResponse:
    return render(request, status=200, template_name='settings/api_key.html')


@login_required
@ui_endpoint_wrapper
def setting_permission(request) -> HttpResponse:
    return render(request, status=200, template_name='settings/permission.html')


def _job_choices() -> list[tuple]:
    # pylint: disable=E1101
    return [(job.id, job.name) for job in Job.objects.all()]


def _user_choices() -> list[tuple]:
    return [(user.id, user.username) for user in User.objects.all()]


def _group_choices() -> list[tuple]:
    return [(group.id, group.name) for group in Group.objects.all()]


class SettingPermissionForm(ModelForm):
    class Meta:
        model = JobPermission
        fields = JobPermission.form_fields
        field_order = JobPermission.form_fields
        labels = FORM_LABEL['settings']['permissions']
        help_texts = FORM_HELP['settings']['permissions']

    jobs = MultipleChoiceField(
        required=False,
        widget=SelectMultiple,
        choices=_job_choices,
    )
    users = MultipleChoiceField(
        required=False,
        widget=SelectMultiple,
        choices=_user_choices,
    )
    groups = MultipleChoiceField(
        required=False,
        widget=SelectMultiple,
        choices=_group_choices,
    )


@login_required
@ui_endpoint_wrapper_kwargs
def setting_permission_edit(request, perm_id: int = None) -> HttpResponse:
    perm_form = SettingPermissionForm()
    form_method = 'post'
    form_api = 'permission'
    perm = {}

    if perm_id is not None and perm_id != 0:
        # pylint: disable=E1101
        perm = JobPermission.objects.filter(id=perm_id).first()
        if perm is None:
            return redirect(f"/ui/settings/permissions?error=Permission with ID {perm_id} does not exist")

        perm = perm.__dict__
        form_method = 'put'
        form_api += f'/{perm_id}'

    perm_form_html = perm_form.render(
        template_name='forms/snippet.html',
        context={'form': perm_form, 'existing': perm},
    )
    return render(
        request, status=200, template_name='settings/permission_edit.html',
        context={'form': perm_form_html, 'form_api': form_api, 'form_method': form_method}
    )


urlpatterns_settings = [
    path('ui/settings/api_keys', setting_api_key),
    path('ui/settings/permissions/<int:perm_id>', setting_permission_edit),
    path('ui/settings/permissions', setting_permission),
]
