from functools import cache

from sys import version_info
from pathlib import Path
from datetime import datetime
from collections import OrderedDict
from importlib import metadata

from aw.config.main import VERSION
from aw.utils.subps import process_cache
from aw.utils.util import datetime_from_db_str
from aw.config.hardcoded import LOG_TIME_FORMAT
from aw.utils.deployment import deployment_docker
from aw.model.system import get_schema_metadata


@cache
def get_version() -> str:
    if VERSION == 'latest' or VERSION.find('dev') != -1 or VERSION.find('staging') != -1:
        this_file = Path(__file__)
        repo_base = this_file.resolve().parent.parent.parent.parent.parent
        if (repo_base / '.git').is_dir():
            commit = process_cache(cmd='git rev-parse --short HEAD', cwd=repo_base)['stdout'].strip()
            if commit != '':
                return f'{VERSION} ({commit})'

        else:
            mod_time = this_file.stat().st_mtime
            mod_time = datetime.fromtimestamp(mod_time).strftime(LOG_TIME_FORMAT)
            return f'{VERSION} ({mod_time})'

    return VERSION


def parsed_ansible_version(python_modules) -> dict:
    versions = {'ansible': None, 'jinja': None, 'libyaml': None, 'ansible_runner': None}
    try:
        ansible_version = process_cache('ansible --version')['stdout'].split('\n')
        versions['ansible_core'] = ansible_version[0].strip()
        versions['jinja'] = ansible_version[-2].split('=')[1].strip()
        versions['libyaml'] = ansible_version[-1].split('=')[1].strip()

        if 'ansible-runner' in python_modules:
            versions['ansible_runner'] = python_modules['ansible-runner']['version']

        if 'ansible' in python_modules:
            versions['ansible'] = python_modules['ansible']['version']

    except IndexError:
        pass

    return versions


def parsed_python_modules() -> dict:
    modules = OrderedDict()
    try:
        module_list = [m[0] for m in metadata.packages_distributions().values()]

        for module in sorted(module_list):
            modules[module.lower()] = {'name': module, 'version': metadata.distribution(module).version}

    except (ImportError, AttributeError):
        result = process_cache('pip list')
        if result['rc'] != 0:
            return {}

        for line in result['stdout'].split('\n'):
            if line.find('.') == -1:
                continue

            name, version = line.split(' ', 1)
            name = name.strip()
            modules[name.lower()] = {'name': name, 'version': version.strip()}

    return modules


def get_system_versions(python_modules: dict = None, ansible_version: dict = None) -> dict:
    if python_modules is None:
        python_modules = parsed_python_modules()

    if ansible_version is None:
        ansible_version = parsed_ansible_version(python_modules)

    linux_versions = process_cache('uname -a')['stdout']
    if deployment_docker():
        linux_versions += ' (dockerized)'

    db_schema = get_schema_metadata()

    return {
        'env_linux': linux_versions,
        'env_db_schema': f'{db_schema.schema_version} (updated: {datetime_from_db_str(db_schema.updated)})',
        'env_git': process_cache('git --version')['stdout'],
        'env_ansible_core': ansible_version['ansible_core'],
        'env_ansible_runner': ansible_version['ansible_runner'],
        'env_django': python_modules['django']['version'],
        'env_django_api': python_modules['djangorestframework']['version'],
        'env_gunicorn': python_modules['gunicorn']['version'],
        'env_jinja': ansible_version['jinja'],
        'env_libyaml': ansible_version['libyaml'],
        'env_python': f"{version_info.major}.{version_info.minor}.{version_info.micro}",
    }
