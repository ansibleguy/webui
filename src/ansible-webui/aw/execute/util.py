from pathlib import Path
from shutil import rmtree
from random import choice as random_choice
from string import digits
from datetime import datetime
from re import sub as regex_replace

from ansible_runner import Runner as AnsibleRunner

from aw.config.main import config, check_config_is_true
from aw.config.hardcoded import FILE_TIME_FORMAT, SHORT_TIME_FORMAT
from aw.utils.util import get_choice_key_by_value, is_set, is_null, datetime_w_tz, datetime_from_db
from aw.utils.handlers import AnsibleConfigError
from aw.model.job import Job, JobExecution, JobExecutionResult, JobExecutionResultHost, \
    CHOICES_JOB_EXEC_STATUS, JobError


def _decode_job_env_vars(env_vars_csv: str, src: str) -> dict:
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


def _runner_options(job: Job, execution: JobExecution) -> dict:
    # NOTES:
    #  playbook str or list
    #  project_dir = playbook_dir
    #  quiet
    #  limit, verbosity, envvars

    # build unique temporary execution directory
    path_run = config['path_run']
    if not path_run.endswith('/'):
        path_run += '/'

    path_run += datetime.now().strftime(FILE_TIME_FORMAT)
    path_run += ''.join(random_choice(digits) for _ in range(5))

    # merge job + execution env-vars
    env_vars = {}
    if is_set(job.environment_vars.strip()):
        env_vars = {
            **env_vars,
            **_decode_job_env_vars(env_vars_csv=job.environment_vars, src='Job')
        }

    if is_set(execution.environment_vars):
        env_vars = {
            **env_vars,
            **_decode_job_env_vars(env_vars_csv=execution.environment_vars, src='Execution')
        }

    verbosity = None
    if execution.verbosity != 0:
        verbosity = execution.verbosity

    elif job.verbosity != 0:
        verbosity = job.verbosity

    opts = {
        'private_data_dir': path_run,
        'project_dir': config['path_play'],
        'quiet': True,
        'limit': execution.limit if is_set(execution.limit) else job.limit,
        'verbosity': verbosity,
        'envvars': env_vars,
        'timeout': config['run_timeout'],
    }

    if check_config_is_true('run_isolate_dir'):
        opts['directory_isolation_base_path'] = path_run / 'play_base'

    if check_config_is_true('run_isolate_process'):
        opts['process_isolation'] = True
        opts['process_isolation_hide_paths'] = config['run_isolate_process_path_hide']
        opts['process_isolation_show_paths'] = config['run_isolate_process_path_show']
        opts['process_isolation_ro_paths'] = config['run_isolate_process_path_ro']

    return opts


def _create_dirs(path: str, desc: str):
    try:
        path = Path(path)

        if not path.is_dir():
            if not path.parent.is_dir():
                path.parent.mkdir(mode=0o775)

            path.mkdir(mode=0o750)

    except (OSError, FileNotFoundError):
        raise OSError(f"Unable to created {desc} directory: '{path}'").with_traceback(None) from None


def runner_prep(job: Job, execution: JobExecution) -> dict:
    update_execution_status(execution, status='Starting')

    opts = _runner_options(job=job, execution=execution)
    opts['playbook'] = job.playbook.split(',')
    opts['inventory'] = job.inventory.split(',')

    # https://docs.ansible.com/ansible/2.8/user_guide/playbooks_best_practices.html#directory-layout
    project_dir = opts['project_dir']
    if not project_dir.endswith('/'):
        project_dir += '/'

    for playbook in opts['playbook']:
        ppf = project_dir + playbook
        if not Path(ppf).is_file():
            raise AnsibleConfigError(f"Configured playbook not found: '{ppf}'").with_traceback(None) from None

    for inventory in opts['inventory']:
        pi = project_dir + inventory
        if not Path(pi).exists():
            raise AnsibleConfigError(f"Configured inventory not found: '{pi}'").with_traceback(None) from None

    _create_dirs(path=opts['private_data_dir'], desc='run')
    _create_dirs(path=config['path_log'], desc='log')

    update_execution_status(execution, status='Running')
    return opts


def runner_cleanup(opts: dict):
    rmtree(opts['private_data_dir'])


def job_logs(job: Job, execution: JobExecution) -> dict:
    safe_job_name = regex_replace(pattern='[^0-9a-zA-Z-_]+', repl='', string=job.name)
    if is_null(execution.user):
        safe_user_name = 'scheduled'
    else:
        safe_user_name = execution.user.replace('.', '_')
        safe_user_name = regex_replace(pattern='[^0-9a-zA-Z-_]+', repl='', string=safe_user_name)

    timestamp = datetime_w_tz().strftime(FILE_TIME_FORMAT)
    log_file = f"{config['path_log']}/{safe_job_name}_{timestamp}_{safe_user_name}"

    return {
        'stdout': f'{log_file}_stdout.log',
        'stderr': f'{log_file}_stderr.log',
    }


def parse_run_result(execution: JobExecution, time_start: datetime, result: AnsibleRunner):
    # events = list(result.events)

    job_result = JobExecutionResult(
        time_start=time_start,
        time_fin=datetime_w_tz(),
        failed=result.errored,
    )
    job_result.save()

    # https://stackoverflow.com/questions/70348314/get-python-ansible-runner-module-stdout-key-value
    for host in result.stats['processed']:
        result_host = JobExecutionResultHost()

        result_host.unreachable = host in result.stats['unreachable']
        result_host.tasks_skipped = result.stats['skipped'][host] if host in result.stats['skipped'] else 0
        result_host.tasks_ok = result.stats['ok'][host] if host in result.stats['ok'] else 0
        result_host.tasks_failed = result.stats['failures'][host] if host in result.stats['failures'] else 0
        result_host.tasks_ignored = result.stats['ignored'][host] if host in result.stats['ignored'] else 0
        result_host.tasks_rescued = result.stats['rescued'][host] if host in result.stats['rescued'] else 0
        result_host.tasks_changed = result.stats['changed'][host] if host in result.stats['changed'] else 0

        if result_host.tasks_failed > 0:
            # todo: create errors
            pass

        result_host.result = job_result
        result_host.save()

    execution.result = job_result
    if job_result.failed:
        update_execution_status(execution, status='Failed')

    else:
        update_execution_status(execution, status='Finished')


def failure(execution: JobExecution, time_start: datetime, error_s: str, error_m: str):
    update_execution_status(execution, status='Failed')
    job_error = JobError(
        short=error_s,
        med=error_m,
    )
    job_error.save()
    job_result = JobExecutionResult(
        time_start=time_start,
        time_fin=datetime_w_tz(),
        failed=True,
        error=job_error,
    )
    job_result.save()
    execution.result = job_result
    execution.save()
