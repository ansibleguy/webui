from os import environ, getcwd
from pathlib import Path
from secrets import choice as random_choice
from string import digits, ascii_letters, punctuation
from datetime import datetime


def inside_docker() -> bool:
    return 'AW_DOCKER' in environ and environ['AW_DOCKER'] == '1'


def _get_existing_ansible_config_file() -> (str, None):
    # https://docs.ansible.com/ansible/latest/reference_appendices/config.html#the-configuration-file

    for file in [
        getcwd() + '/ansible.cfg',
        environ['HOME'] + '/ansible.cfg',
        environ['HOME'] + '/.ansible.cfg',
        '/etc/ansible/ansible.cfg',
    ]:
        if Path(file).is_file():
            return file

    return None


def _get_defaults_docker(var: str) -> any:
    if not inside_docker():
        return None

    return {
        'path_ssh_known_hosts': f'{getcwd()}/known_hosts',
    }[var]


# need to be referenced multiple times without import dependencies
CONFIG_DEFAULTS = {
    'port': 8000,
    'address': '127.0.0.1',
    'run_timeout': 3600,
    'path_run': '/tmp/ansible-webui',
    'path_play': getcwd(),
    'path_log': f"{environ['HOME']}/.local/share/ansible-webui",
    'db': f"{environ['HOME']}/.config/ansible-webui",
    'timezone': datetime.now().astimezone().tzname(),
    'secret': ''.join(random_choice(ascii_letters + digits + punctuation) for _ in range(50)),
    'session_timeout': 12 * 60 * 60,  # 12h
    'path_ansible_config': _get_existing_ansible_config_file(),
    'path_ssh_known_hosts': _get_defaults_docker('path_ssh_known_hosts'),
    'debug': False,
    'logo_url': 'img/logo.svg',
    'ssl_file_key': None,
    'ssl_file_crt': None,
}
