from pathlib import Path
from random import choice as random_choice
from string import digits, ascii_letters, punctuation
from datetime import datetime
from os import remove

from aw.config.main import config
from aw.config.hardcoded import FILE_TIME_FORMAT
from aw.utils.util import get_choice_key_by_value, is_null
from aw.utils.handlers import AnsibleConfigError
from aw.model.job import Job, JobExecution, CHOICES_JOB_EXEC_STATUS
from aw.execute.config import PWD_ATTRS_ARGS


def overwrite_and_delete_file(file: (str, Path)):
    if not isinstance(file, Path):
        file = Path(file)

    if not file.is_file():
        return

    with open(file, 'w', encoding='utf-8') as _file:
        _file.write(''.join(random_choice(ascii_letters + digits + punctuation) for _ in range(50)),)

    remove(file)


def write_pwd_file(job: Job, pwd_attr: str, path_run: Path) -> (str, None):
    if is_null(getattr(job, pwd_attr)):
        return None

    file = f"{path_run}/.aw_{pwd_attr}"
    with open(file, 'w', encoding='utf-8') as _file:
        _file.write(getattr(job, pwd_attr))

    return f"--{PWD_ATTRS_ARGS[pwd_attr]} {file}"


def decode_job_env_vars(env_vars_csv: str, src: str) -> dict:
    try:
        env_vars = {}
        for kv in env_vars_csv.split(','):
            k, v = kv.split('=')
            env_vars[k] = v

        return env_vars

    except ValueError:
        raise AnsibleConfigError(
            f"Environmental variables of {src} are not in a valid format "
            f"(comma-separated key-value pairs). Example: 'key1=val1,key2=val2'"
        ).with_traceback(None) from None


def update_execution_status(execution: JobExecution, status: str):
    execution.status = get_choice_key_by_value(choices=CHOICES_JOB_EXEC_STATUS, value=status)
    execution.save()


def get_path_run() -> Path:
    # build unique temporary execution directory
    path_run = config['path_run']
    if not path_run.endswith('/'):
        path_run += '/'

    path_run += datetime.now().strftime(FILE_TIME_FORMAT)
    path_run += ''.join(random_choice(digits) for _ in range(5))
    return Path(path_run)


def create_dirs(path: (str, Path), desc: str):
    try:
        if not isinstance(path, Path):
            path = Path(path)

        if not path.is_dir():
            if not path.parent.is_dir():
                path.parent.mkdir(mode=0o775)

            path.mkdir(mode=0o750)

    except (OSError, FileNotFoundError):
        raise OSError(f"Unable to created {desc} directory: '{path}'").with_traceback(None) from None
