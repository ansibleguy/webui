from django.urls import path
from django.conf import settings
from django.contrib.auth.models import Group
from django.db.utils import OperationalError
from django.shortcuts import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.forms import ModelForm, MultipleChoiceField, SelectMultiple

from aw.utils.http import ui_endpoint_wrapper, ui_endpoint_wrapper_kwargs
from aw.model.api import AwAPIKey
from aw.model.job import Job, JobPermission
from aw.config.form_metadata import FORM_LABEL, FORM_HELP


@login_required
@ui_endpoint_wrapper
def setting_api_key(request) -> HttpResponse:
    api_key_tokens = [key.name for key in AwAPIKey.objects.filter(user=request.user)]
    return render(
        request, status=200, template_name='settings/api_key.html',
        context={'api_key_tokens': api_key_tokens}
    )


@login_required
@ui_endpoint_wrapper
def setting_permission(request) -> HttpResponse:
    return render(request, status=200, template_name='settings/permission.html')


class SettingPermissionForm(ModelForm):
    class Meta:
        model = JobPermission
        fields = JobPermission.form_fields
        field_order = JobPermission.form_fields
        labels = FORM_LABEL['settings']['permissions']
        help_texts = FORM_HELP['settings']['permissions']

    # pylint: disable=E1101
    try:
        jobs = MultipleChoiceField(
            required=False,
            widget=SelectMultiple,
            choices=((job.id, job.name) for job in Job.objects.all()),
        )
        users = MultipleChoiceField(
            required=False,
            widget=SelectMultiple,
            choices=((user.id, user.username) for user in settings.AUTH_USER_MODEL.objects.all())
        )
        groups = MultipleChoiceField(
            required=False,
            widget=SelectMultiple,
            choices=((group.id, group.name) for group in Group.objects.all())
        )

    except OperationalError:
        # before db migration/initialization
        pass


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
