from pathlib import Path
from shutil import rmtree
from re import sub as regex_replace
from os import symlink
from os import path as os_path
from os import remove as remove_file

from ansible_runner import Runner, RunnerConfig

from aw.config.main import config
from aw.config.hardcoded import FILE_TIME_FORMAT
from aw.utils.util import is_set, is_null, datetime_w_tz, write_file_0640
from aw.model.job import Job, JobExecution, JobExecutionResult, JobExecutionResultHost, JobError
from aw.model.job_credential import BaseJobCredentials
from aw.execute.util import update_execution_status, overwrite_and_delete_file, decode_job_env_vars, \
    create_dirs, is_execution_status, config_error
from aw.utils.debug import log
from aw.execute.play_credentials import get_credentials_to_use, commandline_arguments_credentials, \
    write_pwd_file, get_pwd_file

# see: https://ansible.readthedocs.io/projects/runner/en/latest/intro/


def _exec_log(execution: JobExecution, msg: str, level: int = 3):
    log(
        msg=f"Job-execution '{execution.job}' @ {execution.result.time_start}: {msg}",
        level=level,
    )


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

    credentials = get_credentials_to_use(job=job, execution=execution)
    if credentials is not None:
        cmd_arguments.extend(
            commandline_arguments_credentials(credentials=credentials, path_run=path_run)
        )

    if is_set(config['path_ssh_known_hosts']) and \
            ' '.join(cmd_arguments).find('ansible_ssh_extra_args') == -1:
        if Path(config['path_ssh_known_hosts']).is_file():
            cmd_arguments.append(
                f"-e \"ansible_ssh_extra_args='-o UserKnownHostsFile={config['path_ssh_known_hosts']}'\""
            )

        else:
            _exec_log(execution=execution, msg='Ignoring known_host file because it does not exist', level=5)

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

    credentials = get_credentials_to_use(job=job, execution=execution)
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

    execution.save()
    runner_cleanup(path_run)
