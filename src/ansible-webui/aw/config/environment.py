from os import environ, getcwd
from pathlib import Path
from secrets import choice as random_choice
from string import digits, ascii_letters, punctuation
from datetime import datetime
from functools import cache


AW_ENV_VARS = {
    'timezone': ['AW_TIMEZONE'],
    'secret': ['AW_SECRET'],
    'path_run': ['AW_PATH_RUN'],
    'path_play': ['AW_PATH_PLAY', 'ANSIBLE_PLAYBOOK_DIR'],
    'version': ['AW_VERSION'],
    'deployment': ['AW_ENV'],
    'serve_static': ['AW_SERVE_STATIC'],
    'init_admin': ['AW_ADMIN'],
    'init_admin_pwd': ['AW_ADMIN_PWD'],
    'db': ['AW_DB'],
    'db_migrate': ['AW_DB_MIGRATE'],
    'run_timeout': ['AW_RUN_TIMEOUT'],
    'run_isolate_dir': ['AW_RUN_ISOLATE_DIR'],
    'run_isolate_process': ['AW_RUN_ISOLATE_PS'],
    'run_isolate_process_bin': ['AW_RUN_ISOLATE_PS_EXEC'],  # podman
    'run_isolate_process_path_hide': ['AW_RUN_ISOLATE_PS_PATH_HIDE'],
    'run_isolate_process_path_show': ['AW_RUN_ISOLATE_PS_PATH_SHOW'],
    'run_isolate_process_path_ro': ['AW_RUN_ISOLATE_PS_PATH_RO'],
    'ansible_config': ['ANSIBLE_CONFIG'],
    'path_log': ['AW_PATH_LOG'],
    'session_timeout': ['AW_SESSION_TIMEOUT'],
}

# todo: move typing to config-init
AW_ENV_VARS_TYPING = {
    'csv': [
        'run_isolate_process_path_hide', 'run_isolate_process_path_show', 'run_isolate_process_path_ro',
    ],
}


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


# todo: move static defaults to config-model
AW_ENV_VARS_DEFAULTS = {
    'run_timeout': 3600,
    'path_run': '/tmp/ansible-webui',
    'path_play': getcwd(),
    'path_log': f"{environ['HOME']}/.local/share/ansible-webui",
    'db': f"{environ['HOME']}/.config/ansible-webui",
    'timezone': datetime.now().astimezone().tzname(),
    'secret': ''.join(random_choice(ascii_letters + digits + punctuation) for _ in range(50)),
    'ansible_config': _get_existing_ansible_config_file(),
    'session_timeout': 12 * 60 * 60,  # 12h
}


@cache
def get_aw_env_var(var: str) -> (str, list, None):
    val = AW_ENV_VARS_DEFAULTS.get(var, None)

    for key in AW_ENV_VARS[var]:
        if key in environ:
            val = environ[key]
            break

    if val is None:
        return None

    if var in AW_ENV_VARS_TYPING['csv']:
        return val.split(',')

    return val


def check_aw_env_var_is_set(var: str) -> bool:
    return get_aw_env_var(var) is not None


# only use on edge-cases; as.config.main.check_config_is_true is preferred
def check_aw_env_var_true(var: str, fallback: bool = False) -> bool:
    val = get_aw_env_var(var)
    if val is None:
        return fallback

    return str(val).lower() in ['1', 'true', 'y', 'yes']
