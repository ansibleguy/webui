from django import forms
from django.shortcuts import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from aw.utils.http import ui_endpoint_wrapper_kwargs
from aw.model.permission import JobPermission, JobPermissionMapping, JobCredentialsPermissionMapping, \
    JobRepositoryPermissionMapping, JobPermissionMemberUser, JobPermissionMemberGroup
from aw.model.alert import AlertUser, AlertPlugin, AlertGroup, AlertGlobal
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


class SettingAlertPluginForm(forms.ModelForm):
    class Meta:
        model = AlertPlugin
        fields = AlertPlugin.form_fields
        field_order = AlertPlugin.form_fields


@login_required
@ui_endpoint_wrapper_kwargs
def setting_alert_plugin_edit(request, plugin_id: int = None) -> HttpResponse:
    perm_form = SettingAlertPluginForm()
    form_method = 'post'
    form_api = 'alert/plugin'
    plugin = {}

    if plugin_id is not None and plugin_id != 0:
        plugin = AlertPlugin.objects.filter(id=plugin_id).first()
        if plugin is None:
            return redirect(f"/ui/settings/alerts?error=Alert-Plugin with ID {plugin_id} does not exist")

        plugin = plugin.__dict__
        form_method = 'put'
        form_api += f'/{plugin_id}'

    perm_form_html = perm_form.render(
        template_name='forms/snippet.html',
        context={'form': perm_form, 'existing': plugin},
    )
    return render(
        request, status=200, template_name='settings/alert_edit.html',
        context={'form': perm_form_html, 'form_api': form_api, 'form_method': form_method}
    )


def _choices_alert_user_plugins() -> list:
    return [
        (plugin.id, plugin.name)
        for plugin in AlertUser.objects.all()
    ]


class SettingAlertUserForm(forms.ModelForm):
    class Meta:
        model = AlertUser
        fields = AlertUser.form_fields
        field_order = AlertUser.form_fields
        labels = FORM_LABEL['settings']['alerts']
        help_texts = FORM_HELP['settings']['alerts']

    jobs = forms.MultipleChoiceField(
        required=False,
        widget=forms.SelectMultiple,
        choices=choices_job,
    )
    plugin = forms.ChoiceField(
        required=False,
        widget=forms.Select,
        choices=_choices_alert_user_plugins,
    )


@login_required
@ui_endpoint_wrapper_kwargs
def setting_alert_user_edit(request, alert_id: int = None) -> HttpResponse:
    perm_form = SettingAlertUserForm()
    form_method = 'post'
    form_api = 'alert/user'
    alert = {}

    if alert_id is not None and alert_id != 0:
        alert = AlertUser.objects.filter(id=alert_id).first()
        if alert is None:
            return redirect(f"/ui/settings/alerts?error=Alert with ID {alert_id} does not exist")

        alert = alert.__dict__
        form_method = 'put'
        form_api += f'/{alert_id}'

    perm_form_html = perm_form.render(
        template_name='forms/snippet.html',
        context={'form': perm_form, 'existing': alert},
    )
    return render(
        request, status=200, template_name='settings/alert_edit.html',
        context={'form': perm_form_html, 'form_api': form_api, 'form_method': form_method}
    )


def _choices_alert_group_plugins() -> list:
    return [
        (plugin.id, plugin.name)
        for plugin in AlertGroup.objects.all()
    ]


class SettingAlertGroupForm(forms.ModelForm):
    class Meta:
        model = AlertGroup
        fields = AlertGroup.form_fields
        field_order = AlertGroup.form_fields
        labels = FORM_LABEL['settings']['alerts']
        help_texts = FORM_HELP['settings']['alerts']

    jobs = forms.MultipleChoiceField(
        required=False,
        widget=forms.SelectMultiple,
        choices=choices_job,
    )
    plugin = forms.ChoiceField(
        required=False,
        widget=forms.Select,
        choices=_choices_alert_group_plugins,
    )
    group = forms.ChoiceField(
        required=True,
        widget=forms.Select,
        choices=choices_group,
    )


@login_required
@ui_endpoint_wrapper_kwargs
def setting_alert_group_edit(request, alert_id: int = None) -> HttpResponse:
    perm_form = SettingAlertGroupForm()
    form_method = 'post'
    form_api = 'alert/group'
    alert = {}

    if alert_id is not None and alert_id != 0:
        alert = AlertGroup.objects.filter(id=alert_id).first()
        if alert is None:
            return redirect(f"/ui/settings/alerts?error=Alert with ID {alert_id} does not exist")

        alert = alert.__dict__
        form_method = 'put'
        form_api += f'/{alert_id}'

    perm_form_html = perm_form.render(
        template_name='forms/snippet.html',
        context={'form': perm_form, 'existing': alert},
    )
    return render(
        request, status=200, template_name='settings/alert_edit.html',
        context={'form': perm_form_html, 'form_api': form_api, 'form_method': form_method}
    )


def _choices_alert_global_plugins() -> list:
    return [
        (plugin.id, plugin.name)
        for plugin in AlertGlobal.objects.all()
    ]


class SettingAlertGlobalForm(forms.ModelForm):
    class Meta:
        model = AlertGlobal
        fields = AlertGlobal.form_fields
        field_order = AlertGlobal.form_fields
        labels = FORM_LABEL['settings']['alerts']
        help_texts = FORM_HELP['settings']['alerts']

    jobs = forms.MultipleChoiceField(
        required=False,
        widget=forms.SelectMultiple,
        choices=choices_job,
    )
    plugin = forms.ChoiceField(
        required=False,
        widget=forms.Select,
        choices=_choices_alert_global_plugins,
    )


@login_required
@ui_endpoint_wrapper_kwargs
def setting_alert_global_edit(request, alert_id: int = None) -> HttpResponse:
    perm_form = SettingAlertUserForm()
    form_method = 'post'
    form_api = 'alert/global'
    alert = {}

    if alert_id is not None and alert_id != 0:
        alert = AlertGlobal.objects.filter(id=alert_id).first()
        if alert is None:
            return redirect(f"/ui/settings/alerts?error=Alert with ID {alert_id} does not exist")

        alert = alert.__dict__
        form_method = 'put'
        form_api += f'/{alert_id}'

    perm_form_html = perm_form.render(
        template_name='forms/snippet.html',
        context={'form': perm_form, 'existing': alert},
    )
    return render(
        request, status=200, template_name='settings/alert_edit.html',
        context={'form': perm_form_html, 'form_api': form_api, 'form_method': form_method}
    )
