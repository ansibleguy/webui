from os import environ, getcwd
from pathlib import Path
from secrets import choice as random_choice
from string import digits, ascii_letters, punctuation
from datetime import datetime


def get_existing_ansible_config_file() -> str:
    # https://docs.ansible.com/ansible/latest/reference_appendices/config.html#the-configuration-file

    for file in [
        getcwd() + '/ansible.cfg',
        environ['HOME'] + '/ansible.cfg',
        environ['HOME'] + '/.ansible.cfg',
    ]:
        if Path(file).is_file():
            return file

    return '/etc/ansible/ansible.cfg'


ENVIRON_FALLBACK = {
    'timezone': {'keys': ['AW_TIMEZONE', 'TZ'], 'fallback': datetime.now().astimezone().tzname()},
    '_secret': {
        'keys': ['AW_SECRET'],
        'fallback': ''.join(random_choice(ascii_letters + digits + punctuation) for _ in range(50))
    },
    'path_base': {'keys': ['AW_PATH_BASE'], 'fallback': '/tmp/ansible-webui'},
    'path_play': {'keys': ['AW_PATH_PLAY', 'ANSIBLE_PLAYBOOK_DIR'], 'fallback': getcwd()},
    'ansible_config': {'keys': ['ANSIBLE_CONFIG'], 'fallback': get_existing_ansible_config_file()}
}
