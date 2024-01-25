from pathlib import Path
from shutil import rmtree
from datetime import datetime
from re import sub as regex_replace

from ansible_runner import Runner as AnsibleRunner

from aw.config.main import config, check_config_is_true
from aw.config.hardcoded import FILE_TIME_FORMAT
from aw.utils.util import is_set, is_null, datetime_w_tz
from aw.utils.handlers import AnsibleConfigError
from aw.model.job import Job, JobExecution, JobExecutionResult, JobExecutionResultHost, \
    JobError
from aw.execute.util import update_execution_status, write_pwd_file, overwrite_and_delete_file, \
    decode_job_env_vars, create_dirs
from aw.execute.config import PWD_ATTRS
from aw.utils.debug import log

# see: https://ansible.readthedocs.io/projects/runner/en/latest/intro/


def _commandline_arguments(job: Job, path_run: Path) -> str:
    cmd_arguments = []
    if is_set(job.cmd_args):
        cmd_arguments.append(job.cmd_args)

    for attr, flag in {
        'connect_user': '-u',
        'become_user': '--become-user',
        'vault_file': '--vault-password-file',
        'vault_id': '--vault-id',
    }.items():
        if is_set(getattr(job, attr)):
            cmd_arguments.append(f'{flag} {getattr(job, attr)}')

    if job.mode_check:
        cmd_arguments.append('--check')

    if job.mode_diff:
        cmd_arguments.append('--diff')

    for attr in PWD_ATTRS:
        pwd_arg = write_pwd_file(job=job, pwd_attr=attr, path_run=path_run)
        if pwd_arg is not None:
            cmd_arguments.append(pwd_arg)

    return ' '.join(cmd_arguments)


def _execution_or_job(job: Job, execution: JobExecution, attr: str):
    exec_val = getattr(execution, attr)
    if is_set(exec_val):
        return exec_val

    job_val = getattr(job, attr)
    if is_set(job_val):
        return job_val

    return None


def _runner_options(job: Job, execution: JobExecution, path_run: Path) -> dict:
    # merge job + execution env-vars
    env_vars = {}
    if is_set(job.environment_vars.strip()):
        env_vars = {
            **env_vars,
            **decode_job_env_vars(env_vars_csv=job.environment_vars, src='Job')
        }

    if is_set(execution.environment_vars):
        env_vars = {
            **env_vars,
            **decode_job_env_vars(env_vars_csv=execution.environment_vars, src='Execution')
        }

    verbosity = None
    if execution.verbosity != 0:
        verbosity = execution.verbosity

    elif job.verbosity != 0:
        verbosity = job.verbosity

    cmdline_args = _commandline_arguments(job=job, path_run=path_run)
    opts = {
        'private_data_dir': path_run,
        'project_dir': config['path_play'],
        'quiet': True,
        'limit': _execution_or_job(job, execution, 'limit'),
        'tags': _execution_or_job(job, execution, 'tags'),
        'skip_tags': _execution_or_job(job, execution, 'tags_skip'),
        'verbosity': verbosity,
        'envvars': env_vars,
        'timeout': config['run_timeout'],
        'cmdline': cmdline_args if is_set(cmdline_args) else None,
    }

    if is_set(cmdline_args):
        log(msg=f"Custom commandline arguments: '{cmdline_args}'", level=5)

    if check_config_is_true('run_isolate_dir'):
        opts['directory_isolation_base_path'] = path_run / 'play_base'

    if check_config_is_true('run_isolate_process'):
        opts['process_isolation'] = True
        opts['process_isolation_hide_paths'] = config['run_isolate_process_path_hide']
        opts['process_isolation_show_paths'] = config['run_isolate_process_path_show']
        opts['process_isolation_ro_paths'] = config['run_isolate_process_path_ro']

    return opts


def runner_prep(job: Job, execution: JobExecution, path_run: Path) -> dict:
    update_execution_status(execution, status='Starting')

    opts = _runner_options(job=job, execution=execution, path_run=path_run)
    opts['playbook'] = job.playbook
    opts['inventory'] = job.inventory.split(',')

    # https://docs.ansible.com/ansible/2.8/user_guide/playbooks_best_practices.html#directory-layout
    project_dir = opts['project_dir']
    if not project_dir.endswith('/'):
        project_dir += '/'

    ppf = project_dir + opts['playbook']
    if not Path(ppf).is_file():
        raise AnsibleConfigError(f"Configured playbook not found: '{ppf}'").with_traceback(None) from None

    for inventory in opts['inventory']:
        pi = project_dir + inventory
        if not Path(pi).exists():
            raise AnsibleConfigError(f"Configured inventory not found: '{pi}'").with_traceback(None) from None

    create_dirs(path=path_run, desc='run')
    create_dirs(path=config['path_log'], desc='log')

    update_execution_status(execution, status='Running')
    return opts


def runner_cleanup(path_run: Path):
    overwrite_and_delete_file(f"{path_run}/env/passwords")
    for _ in range(10):
        for attr in PWD_ATTRS:
            overwrite_and_delete_file(f"{path_run}/.aw_{attr}")

    rmtree(path_run, ignore_errors=True)


def job_logs(job: Job, execution: JobExecution) -> dict:
    safe_job_name = regex_replace(pattern='[^0-9a-zA-Z-_]+', repl='', string=job.name)
    if is_null(execution.user):
        safe_user_name = 'scheduled'
    else:
        safe_user_name = execution.user.username.replace('.', '_')
        safe_user_name = regex_replace(pattern='[^0-9a-zA-Z-_]+', repl='', string=safe_user_name)

    timestamp = datetime_w_tz().strftime(FILE_TIME_FORMAT)
    log_file = f"{config['path_log']}/{safe_job_name}_{timestamp}_{safe_user_name}"

    return {
        'stdout': f'{log_file}_stdout.log',
        'stderr': f'{log_file}_stderr.log',
    }


def parse_run_result(execution: JobExecution, time_start: datetime, runner: AnsibleRunner):
    job_result = JobExecutionResult(
        time_start=time_start,
        time_fin=datetime_w_tz(),
        failed=runner.errored,
    )
    job_result.save()

    # https://stackoverflow.com/questions/70348314/get-python-ansible-runner-module-stdout-key-value
    for host in runner.stats['processed']:
        result_host = JobExecutionResultHost(hostname=host)

        result_host.unreachable = host in runner.stats['dark']
        result_host.tasks_skipped = runner.stats['skipped'][host] if host in runner.stats['skipped'] else 0
        result_host.tasks_ok = runner.stats['ok'][host] if host in runner.stats['ok'] else 0
        result_host.tasks_failed = runner.stats['failures'][host] if host in runner.stats['failures'] else 0
        result_host.tasks_ignored = runner.stats['ignored'][host] if host in runner.stats['ignored'] else 0
        result_host.tasks_rescued = runner.stats['rescued'][host] if host in runner.stats['rescued'] else 0
        result_host.tasks_changed = runner.stats['changed'][host] if host in runner.stats['changed'] else 0

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


def failure(execution: JobExecution, path_run: Path, time_start: datetime, error_s: str, error_m: str):
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
    runner_cleanup(path_run)
