from pathlib import Path
from shutil import rmtree
from re import sub as regex_replace
from os import symlink
from os import path as os_path
from os import remove as remove_file

from ansible_runner import Runner, RunnerConfig
from django.core.exceptions import ObjectDoesNotExist

from aw.config.main import config, check_config_is_true
from aw.config.hardcoded import FILE_TIME_FORMAT
from aw.utils.util import is_set, is_null, datetime_w_tz, write_file_0640
from aw.model.job import Job, JobExecution, JobExecutionResult, JobExecutionResultHost, JobError
from aw.model.job_credential import BaseJobCredentials, JobUserCredentials
from aw.execute.util import update_execution_status, overwrite_and_delete_file, decode_job_env_vars, \
    create_dirs, get_pwd_file, get_pwd_file_arg, write_pwd_file, is_execution_status, config_error
from aw.utils.permission import has_credentials_permission, CHOICE_PERMISSION_READ
from aw.base import USERS
# from aw.utils.debug import log_warn

# see: https://ansible.readthedocs.io/projects/runner/en/latest/intro/


def _commandline_arguments_credentials(credentials: BaseJobCredentials, path_run: Path) -> list:
    cmd_arguments = []

    for attr, flag in BaseJobCredentials.PUBLIC_ATTRS_ARGS.items():
        if is_set(getattr(credentials, attr)):
            cmd_arguments.append(f'{flag} {getattr(credentials, attr)}')

    for attr in BaseJobCredentials.SECRET_ATTRS:
        pwd_arg = get_pwd_file_arg(credentials, attr=attr, path_run=path_run)
        if pwd_arg is not None:
            cmd_arguments.append(pwd_arg)

    return cmd_arguments


def _scheduled_or_has_credentials_access(user: USERS, credentials: BaseJobCredentials) -> bool:
    if user is None:
        # scheduled execution
        return True

    return has_credentials_permission(
        user=user,
        credentials=credentials,
        permission_needed=CHOICE_PERMISSION_READ,
    )


def _get_credentials_to_use(job: Job, execution: JobExecution) -> (BaseJobCredentials, None):
    credentials = None

    # todo: write warn log if user tried to execute job using non-permitted credentials (if execution.cred*)
    if execution.user is not None and is_set(execution.credential_user) and \
            execution.credential_user.user.id == execution.user.id:
        credentials = execution.credential_user

    elif is_set(execution.credential_global) and _scheduled_or_has_credentials_access(
        user=execution.user, credentials=execution.credential_global,
    ):
        credentials = execution.credential_global

    elif is_set(job.credentials_default) and _scheduled_or_has_credentials_access(
        user=execution.user, credentials=job.credentials_default,
    ):
        credentials = job.credentials_default

    elif job.credentials_needed and is_set(execution.user):
        # try to get default user-credentials as a last-resort if the job needs some credentials
        try:
            credentials = JobUserCredentials.objects.filter(user=execution.user).first()

        except ObjectDoesNotExist:
            pass

    if job.credentials_needed and credentials is None:
        config_error(
            'The job is set to require credentials - but none were provided or readable! '
            'Make sure you have privileges for the configured credentials or create user-specific ones.'
        )

    return credentials


def _commandline_arguments(job: Job, execution: JobExecution, path_run: Path) -> str:
    cmd_arguments = []
    if is_set(job.cmd_args):
        cmd_arguments.append(job.cmd_args)

    if is_set(execution.cmd_args):
        cmd_arguments.append(execution.cmd_args)

    if execution.mode_check:
        cmd_arguments.append('--check')

    if execution.mode_diff:
        cmd_arguments.append('--diff')

    credentials = _get_credentials_to_use(job=job, execution=execution)
    if credentials is not None:
        cmd_arguments.extend(
            _commandline_arguments_credentials(credentials=credentials, path_run=path_run)
        )

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

    cmdline_args = _commandline_arguments(job=job, execution=execution, path_run=path_run)

    opts = {
        'private_data_dir': path_run,
        'limit': _execution_or_job(job, execution, 'limit'),
        'tags': _execution_or_job(job, execution, 'tags'),
        'skip_tags': _execution_or_job(job, execution, 'tags_skip'),
        'verbosity': verbosity,
        'envvars': env_vars,
        'cmdline': cmdline_args if is_set(cmdline_args) else None,
    }

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
    opts['playbook'] = job.playbook_file
    opts['inventory'] = job.inventory_file.split(',')

    # https://docs.ansible.com/ansible/2.8/user_guide/playbooks_best_practices.html#directory-layout
    project_dir = config['path_play']
    if not project_dir.endswith('/'):
        project_dir += '/'

    ppf = project_dir + opts['playbook']
    if not Path(ppf).is_file():
        config_error(f"Configured playbook not found: '{ppf}'")

    for inventory in opts['inventory']:
        pi = project_dir + inventory
        if not Path(pi).exists():
            config_error(f"Configured inventory not found: '{pi}'")

    create_dirs(path=path_run, desc='run')
    create_dirs(path=config['path_log'], desc='log')

    credentials = _get_credentials_to_use(job=job, execution=execution)
    for secret_attr in BaseJobCredentials.SECRET_ATTRS:
        write_pwd_file(credentials, attr=secret_attr, path_run=path_run)

    update_execution_status(execution, status='Running')
    return opts


def runner_logs(cfg: RunnerConfig, log_files: dict):
    logs_src = {
        'stdout': os_path.join(cfg.artifact_dir, 'stdout'),
        'stderr': os_path.join(cfg.artifact_dir, 'stderr'),
    }

    for log_file in log_files.values():
        write_file_0640(file=log_file, content='')

    # link logs from artifacts to log-directory; have not found a working way of overriding the target files..
    for log_type in ['stdout', 'stderr']:
        try:
            symlink(log_files[log_type], logs_src[log_type])

        except FileExistsError:
            remove_file(logs_src[log_type])
            symlink(log_files[log_type], logs_src[log_type])


def runner_cleanup(path_run: Path):
    overwrite_and_delete_file(f"{path_run}/env/passwords")
    for attr in BaseJobCredentials.SECRET_ATTRS:
        overwrite_and_delete_file(get_pwd_file(path_run=path_run, attr=attr))

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


def _run_stats(runner: Runner, result: JobExecutionResult) -> bool:
    any_task_failed = False
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
            any_task_failed = True
            # todo: create errors

        result_host.result = result
        result_host.save()

    return any_task_failed


def parse_run_result(execution: JobExecution, result: JobExecutionResult, runner: Runner):
    result.time_fin = datetime_w_tz()
    result.failed = runner.errored
    result.save()

    any_task_failed = False
    if runner.stats is not None:
        any_task_failed = _run_stats(runner=runner, result=result)

    execution.result = result
    if result.failed or any_task_failed:
        update_execution_status(execution, status='Failed')

    else:
        status = 'Finished'
        if is_execution_status(execution, 'Stopping'):
            status = 'Stopped'

        update_execution_status(execution, status=status)


def failure(
        execution: JobExecution, path_run: Path,
        result: JobExecutionResult, error_s: str, error_m: str
):
    update_execution_status(execution, status='Failed')
    job_error = JobError(
        short=error_s,
        med=error_m,
    )
    job_error.save()
    result.time_fin = datetime_w_tz()
    result.failed = True
    result.error = job_error
    result.save()

    execution.result = result
    execution.save()
    runner_cleanup(path_run)
