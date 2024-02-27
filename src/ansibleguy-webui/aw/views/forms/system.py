from pytz import all_timezones
from django import forms
from django.shortcuts import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from aw.config.main import config
from aw.config.defaults import CONFIG_DEFAULTS
from aw.utils.http import ui_endpoint_wrapper
from aw.config.form_metadata import FORM_LABEL, FORM_HELP
from aw.config.environment import AW_ENV_VARS, AW_ENV_VARS_SECRET
from aw.model.system import SystemConfig
from aw.utils.deployment import deployment_dev


class SystemConfigForm(forms.ModelForm):
    class Meta:
        model = SystemConfig
        fields = SystemConfig.form_fields
        field_order = SystemConfig.form_fields
        labels = FORM_LABEL['system']['config']
        help_texts = FORM_HELP['system']['config']

    path_run = forms.CharField(max_length=500, initial=CONFIG_DEFAULTS['path_run'], required=True)
    path_play = forms.CharField(max_length=500, initial=CONFIG_DEFAULTS['path_play'], required=True)
    path_log = forms.CharField(max_length=500, initial=CONFIG_DEFAULTS['path_log'], required=True)
    path_ansible_config = forms.CharField(
        max_length=500, initial=CONFIG_DEFAULTS['path_ansible_config'], required=False,
    )
    path_ssh_known_hosts = forms.CharField(
        max_length=500, initial=CONFIG_DEFAULTS['path_ssh_known_hosts'], required=False,
    )
    timezone = forms.ChoiceField(
        required=False,
        widget=forms.Select,
        choices=[(tz, tz) for tz in sorted(all_timezones)],
        label=FORM_LABEL['system']['config']['timezone'],
    )
    debug = forms.BooleanField(initial=CONFIG_DEFAULTS['debug'] or deployment_dev())


@login_required
@ui_endpoint_wrapper
def system_config(request) -> HttpResponse:
    config_form = SystemConfigForm()
    form_method = 'put'
    form_api = 'config'

    config_form_html = config_form.render(
        template_name='forms/snippet.html',
        context={'form': config_form, 'existing': {
            key: config[key] for key in SystemConfig.form_fields
        }},
    )
    return render(
        request, status=200, template_name='system/config.html',
        context={
            'form': config_form_html, 'form_api': form_api, 'form_method': form_method,
            'env_vars': AW_ENV_VARS, 'env_labels': FORM_LABEL['system']['config'],
            'env_vars_secret': AW_ENV_VARS_SECRET,
            'env_vars_config': {key: config[key] for key in AW_ENV_VARS},
        }
    )
