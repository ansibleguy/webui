from django import forms
from django.shortcuts import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from aw.utils.http import ui_endpoint_wrapper_kwargs
from aw.model.permission import JobPermission, JobPermissionMapping, JobCredentialsPermissionMapping, \
    JobRepositoryPermissionMapping, JobPermissionMemberUser, JobPermissionMemberGroup
from aw.config.form_metadata import FORM_LABEL, FORM_HELP
from aw.views.base import choices_global_credentials, choices_job, choices_user, choices_group, choices_repositories


class SettingPermissionForm(forms.ModelForm):
    class Meta:
        model = JobPermission
        fields = JobPermission.form_fields
        field_order = JobPermission.form_fields
        labels = FORM_LABEL['settings']['permissions']
        help_texts = FORM_HELP['settings']['permissions']

    users = forms.MultipleChoiceField(
        required=False,
        widget=forms.SelectMultiple,
        choices=choices_user,
    )
    groups = forms.MultipleChoiceField(
        required=False,
        widget=forms.SelectMultiple,
        choices=choices_group,
    )
    jobs = forms.MultipleChoiceField(
        required=False,
        widget=forms.SelectMultiple,
        choices=choices_job,
    )
    credentials = forms.MultipleChoiceField(
        required=False,
        widget=forms.SelectMultiple,
        choices=choices_global_credentials,
    )
    repositories = forms.MultipleChoiceField(
        required=False,
        widget=forms.SelectMultiple,
        choices=choices_repositories,
    )


@login_required
@ui_endpoint_wrapper_kwargs
def setting_permission_edit(request, perm_id: int = None) -> HttpResponse:
    perm_form = SettingPermissionForm()
    form_method = 'post'
    form_api = 'permission'
    perm = {}

    if perm_id is not None and perm_id != 0:
        perm = JobPermission.objects.filter(id=perm_id).first()
        if perm is None:
            return redirect(f"/ui/settings/permissions?error=Permission with ID {perm_id} does not exist")

        data = perm.__dict__
        data['users'] = [link.user.id for link in JobPermissionMemberUser.objects.filter(permission=perm)]
        data['groups'] = [link.group.id for link in JobPermissionMemberGroup.objects.filter(permission=perm)]
        data['jobs'] = [link.job.id for link in JobPermissionMapping.objects.filter(permission=perm)]
        data['credentials'] = [
            link.credentials.id for link in JobCredentialsPermissionMapping.objects.filter(permission=perm)
        ]
        data['repositories'] = [
            link.repository.id for link in JobRepositoryPermissionMapping.objects.filter(permission=perm)
        ]
        perm = data
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
