from pathlib import Path
from shutil import rmtree
from os import symlink
from os import path as os_path
from os import remove as remove_file
from os import stat as os_stat

from ansible_runner import Runner, RunnerConfig
try:
    from ara.setup.callback_plugins import callback_plugins as ara_callback_plugins

except (ImportError, ModuleNotFoundError):
    ara_callback_plugins = None

from aw.config.main import config
from aw.utils.util import is_set, datetime_w_tz, write_file_0640
from aw.model.job import Job, JobExecution, JobExecutionResult, JobExecutionResultHost, JobError
from aw.model.job_credential import BaseJobCredentials
from aw.execute.util import update_status, overwrite_and_delete_file, decode_job_env_vars, \
    create_dirs, is_execution_status, config_error
from aw.utils.debug import log
from aw.execute.play_credentials import get_credentials_to_use, commandline_arguments_credentials, \
    write_pwd_file, get_pwd_file
from aw.execute.repository import ExecuteRepository

# see: https://ansible.readthedocs.io/projects/runner/en/latest/intro/


def _exec_log(execution: JobExecution, msg: str, level: int = 3):
    # todo: add execution logs to UI (?)
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

    if execution.mode_check or job.mode_check:
        cmd_arguments.append('--check')

    if execution.mode_diff or job.mode_diff:
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


def _environmental_variables(job: Job, execution: JobExecution) -> dict:
    # merge global, job + execution env-vars
    env_vars = {}
    if is_set(config['ara_server']):
        if ara_callback_plugins is None:
            _exec_log(
                execution=execution,
                msg="Ignoring 'ara_server' setting because 'ara' module is not installed'",
                level=3,
            )

        else:
            env_vars['ANSIBLE_CALLBACK_PLUGINS'] = ara_callback_plugins
            env_vars['ARA_API_CLIENT'] = 'http'
            env_vars['ARA_API_SERVER'] = config['ara_server']

    if is_set(config['global_environment_vars']):
        env_vars = {
            **env_vars,
            **decode_job_env_vars(env_vars_csv=config['global_environment_vars'], src='Global')
        }

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

    return env_vars


def _execution_or_job(job: Job, execution: JobExecution, attr: str):
    exec_val = getattr(execution, attr)
    if is_set(exec_val):
        return exec_val

    job_val = getattr(job, attr)
    if is_set(job_val):
        return job_val

    return None


def _runner_options(job: Job, execution: JobExecution, path_run: Path, project_dir: str) -> dict:
    verbosity = None
    if execution.verbosity != 0:
        verbosity = execution.verbosity

    elif job.verbosity != 0:
        verbosity = job.verbosity

    cmdline_args = _commandline_arguments(job=job, execution=execution, path_run=path_run)

    opts = {
        'project_dir': project_dir,
        'private_data_dir': path_run,
        'limit': _execution_or_job(job, execution, 'limit'),
        'tags': _execution_or_job(job, execution, 'tags'),
        'skip_tags': _execution_or_job(job, execution, 'tags_skip'),
        'verbosity': verbosity,
        'envvars': _environmental_variables(job=job, execution=execution),
        'cmdline': cmdline_args if is_set(cmdline_args) else None,
    }

    return opts


def runner_prep(job: Job, execution: JobExecution, path_run: Path, project_dir: str) -> dict:
    update_status(execution, status='Starting')

    opts = _runner_options(job=job, execution=execution, path_run=path_run, project_dir=project_dir)
    opts['playbook'] = job.playbook_file
    if is_set(job.inventory_file):
        opts['inventory'] = job.inventory_file.split(',')

    # https://docs.ansible.com/ansible/2.8/user_guide/playbooks_best_practices.html#directory-layout
    ppf = Path(opts['project_dir']) / opts['playbook']
    if not Path(ppf).is_file():
        config_error(f"Configured playbook not found: '{ppf}'")

    if 'inventory' in opts:
        for inventory in opts['inventory']:
            pi = Path(opts['project_dir']) / inventory
            if not Path(pi).exists():
                config_error(f"Configured inventory not found: '{pi}'")

    create_dirs(path=path_run, desc='run')
    create_dirs(path=config['path_log'], desc='log')

    credentials = get_credentials_to_use(job=job, execution=execution)
    for secret_attr in BaseJobCredentials.SECRET_ATTRS:
        write_pwd_file(credentials, attr=secret_attr, path_run=path_run)

    update_status(execution, status='Running')
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


def runner_cleanup(execution: JobExecution, path_run: Path, exec_repo: ExecuteRepository):
    overwrite_and_delete_file(f"{path_run}/env/passwords")
    overwrite_and_delete_file(f"{path_run}/env/ssh_key")
    for attr in BaseJobCredentials.SECRET_ATTRS:
        overwrite_and_delete_file(get_pwd_file(path_run=path_run, attr=attr))

    try:
        exec_repo.cleanup_repository()

    except AttributeError as err:
        log(msg=f'Got error of repository cleanup: {err}')

    # clean empty log files
    for log_file in JobExecution.log_file_fields:
        log_file_path = getattr(execution, log_file)
        try:
            if os_stat(log_file_path).st_size == 0:
                remove_file(log_file_path)

        except (FileNotFoundError, TypeError):
            pass

    rmtree(path_run, ignore_errors=True)


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

        if result_host.unreachable:
            any_task_failed = True

        elif result_host.tasks_failed > 0:
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

    if runner.errored or runner.timed_out or runner.rc != 0 or any_task_failed:
        update_status(execution, status='Failed')

    else:
        status = 'Finished'
        if is_execution_status(execution, 'Stopping') or runner.canceled:
            status = 'Stopped'

        update_status(execution, status=status)


def failure(
        execution: JobExecution, exec_repo: ExecuteRepository, path_run: Path,
        result: JobExecutionResult, error_s: str, error_m: str
):
    update_status(execution, status='Failed')
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
    runner_cleanup(execution=JobExecution ,path_run=path_run, exec_repo=exec_repo)
