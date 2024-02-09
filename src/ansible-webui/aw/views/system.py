from sys import version_info
from importlib import metadata

from django.urls import path
from django.shortcuts import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ansible_runner.interface import get_ansible_config

from aw.utils.http import ui_endpoint_wrapper
from aw.utils.subps import process


def _parsed_ansible_collections() -> dict:
    collections_raw = process(['ansible-galaxy', 'collection', 'list'])['stdout']
    collections = {}
    col_counter = {}
    collection_path = ''
    for line in collections_raw.split('\n'):
        if line.startswith('#'):
            collection_path = line[1:]
            continue

        if line.find('.') == -1:
            continue

        name, version = line.split(' ', 1)
        name, version = name.strip(), version.strip()
        if name in collections:
            if name in col_counter:
                col_counter[name] += 1
            else:
                col_counter[name] = 2

            name = f'{name} ({col_counter[name]})'

        collections[name] = {'version': version, 'path': collection_path}

    return dict(sorted(collections.items()))


def _parsed_ansible_config() -> dict:
    config_raw = get_ansible_config(action='dump')[0].split('\n')
    config = {}

    for line in config_raw:
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

        config[setting] = {'value': value, 'comment': comment}

    return dict(sorted(config.items()))


@login_required
@ui_endpoint_wrapper
def system_environment(request) -> HttpResponse:
    # todo: allow to check for updates (pypi, ansible-galaxy & github api)

    return render(
        request, status=200, template_name='system/environment.html',
        context={
            'env_linux': process(['uname', '-a'])['stdout'],
            'env_python': f"{version_info.major}.{version_info.minor}.{version_info.micro}",
            'env_pip': dict(sorted(
                {p.metadata['Name']: p.metadata['Version'] for p in metadata.distributions()}.items()
            )),
            'env_ansible_config': _parsed_ansible_config(),
            # 'env_ansible_roles': get_role_list(),
            'env_ansible_collections': _parsed_ansible_collections(),
        }
    )


urlpatterns_system = [
    path('ui/system/environment', system_environment),
]
