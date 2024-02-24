from os import environ
from pathlib import Path
from getpass import getuser

from pytz import all_timezones
from django import forms
from django.urls import path
from django.shortcuts import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ansible_runner.interface import get_ansible_config

from aw.config.main import config
from aw.config.defaults import CONFIG_DEFAULTS
from aw.utils.http import ui_endpoint_wrapper
from aw.utils.subps import process_cache
from aw.config.form_metadata import FORM_LABEL, FORM_HELP
from aw.config.environment import AW_ENV_VARS, AW_ENV_VARS_SECRET
from aw.model.system import SystemConfig
from aw.utils.version import get_system_versions, parsed_ansible_version, parsed_python_modules
from aw.utils.deployment import deployment_dev


def _parsed_ansible_collections() -> dict:
    result = process_cache('ansible-galaxy collection list')
    if result['rc'] != 0:
        return {}

    collections = {}
    col_counter = {}
    collection_path = ''
    for line in result['stdout'].split('\n'):
        if line.startswith('#'):
            collection_path = line[1:]
            continue

        if line.find('.') == -1:
            continue

        name, version = line.split(' ', 1)
        name, version = name.strip(), version.strip()
        url = f"https://galaxy.ansible.com/ui/repo/published/{name.replace('.', '/')}"

        if name in collections:
            if name in col_counter:
                col_counter[name] += 1
            else:
                col_counter[name] = 2

            name = f'{name} ({col_counter[name]})'

        collections[name] = {'version': version, 'path': collection_path, 'url': url}

    return dict(sorted(collections.items()))


def _parsed_ansible_config() -> dict:
    environ['ANSIBLE_FORCE_COLOR'] = '0'
    ansible_config_raw = get_ansible_config(action='dump', quiet=True)[0].split('\n')
    environ['ANSIBLE_FORCE_COLOR'] = '1'
    ansible_config = {}

    for line in ansible_config_raw:
        try:
            setting_comment, value = line.split('=', 1)

        except ValueError:
            continue

        setting_comment, value = setting_comment.strip(), value.strip()
        try:
            setting, comment = setting_comment.rsplit('(', 1)
            comment = comment.replace(')', '')

        except ValueError:
            setting, comment = setting_comment, '-'

        url = ("https://docs.ansible.com/ansible/latest/reference_appendices/config.html#"
               f"{setting.lower().replace('_', '-')}")

        ansible_config[setting] = {'value': value, 'comment': comment, 'url': url}

    return dict(sorted(ansible_config.items()))


def _aws_ssm() -> (str, None):
    if Path('/usr/bin/session-manager-plugin').is_file():
        return process_cache('/usr/bin/session-manager-plugin --version')['stdout']

    return None


@login_required
@ui_endpoint_wrapper
def system_environment(request) -> HttpResponse:
    # todo: allow to check for updates (pypi, ansible-galaxy & github api)
    python_modules = parsed_python_modules()
    ansible_version = parsed_ansible_version(python_modules)
    env_system = get_system_versions(python_modules=python_modules, ansible_version=ansible_version)

    return render(
        request, status=200, template_name='system/environment.html',
        context={
            **env_system,
            'env_user': getuser(),
            'env_system': env_system,
            'env_aws_ssm': _aws_ssm(),
            'env_python_modules': python_modules,
            'env_ansible_config': _parsed_ansible_config(),
            # 'env_ansible_roles': get_role_list(),
            'env_ansible_collections': _parsed_ansible_collections(),
        },
    )


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


urlpatterns_system = [
    path('ui/system/environment', system_environment),
    path('ui/system/config', system_config),
]
