from pathlib import Path
from shutil import rmtree

from aw.config.main import config
from aw.model.job import Job, JobExecution
from aw.utils.util import is_null, is_set, write_file_0640
from aw.utils.subps import process
from aw.execute.play_credentials import write_pwd_file, get_pwd_file
from aw.execute.util import overwrite_and_delete_file
from aw.model.job_credential import BaseJobCredentials
from aw.utils.handlers import AnsibleRepositoryError


def repo_error(msg: str):
    raise AnsibleRepositoryError(msg).with_traceback(None) from None


def get_path_run_repo(path_run: Path) -> Path:
    return path_run / '.repository'


def get_path_repo(job: Job, execution: JobExecution) -> Path:
    if job.repository.rtype_name == 'Static':
        return job.repository.static_path

    path_repo = Path(config['path_run']) / 'repositories' / job.repository.name
    if not path_repo.parent.is_dir():
        path_repo.parent.mkdir(mode=0o750)

    if not path_repo.is_dir():
        path_repo.mkdir(mode=0o750)

    if job.repository.git_isolate:
        path_repo = path_repo / job.id / execution.id

        if not path_repo.parent.is_dir():
            path_repo.parent.mkdir(mode=0o750)

        if not path_repo.is_dir():
            path_repo.mkdir(mode=0o750)

    return path_repo


def get_path_playbook_base(job: Job, execution: JobExecution) -> Path:
    path_repo = get_path_repo(job=job, execution=execution)
    if job.repository.rtype_name == 'Git' and is_set(job.repository.git_playbook_base):
        path_repo = path_repo / job.repository.git_playbook_base

    return path_repo


def get_project_dir(job: Job, execution: JobExecution) -> str:
    if is_null(job.repository):
        return config['path_play']

    return str(get_path_playbook_base(job=job, execution=execution))


def _repo_process(cmd: (str, list), path_repo: Path, env: dict, execution: JobExecution):
    if isinstance(cmd, str):
        cmd_str = cmd
        cmd = cmd.split(' ')
    else:
        cmd_str = ' '.join(cmd)

    result = process(cmd=cmd, cwd=path_repo, env=env)
    write_file_0640(
        file=execution.log_stdout_repo,
        content=f"\nCOMMAND: {cmd_str}\n{result['stdout']}"
    )
    write_file_0640(
        file=execution.log_stderr_repo,
        content=f"\nCOMMAND: {cmd_str}\n{result['stderr']}"
    )
    if result['rc'] != 0:
        raise repo_error(
            f"Repository command failed: '{cmd_str}'\n"
            f"Got error: '{result['stderr']}'\n"
            f"Got output: '{result['stdout']}'"
        )


def _run_repo_config_cmds(cmds: str, path_repo: Path, env: dict, execution: JobExecution):
    if is_set(cmds):
        for cmd in cmds.split(','):
            _repo_process(cmd=cmd, path_repo=path_repo, env=env, execution=execution)


def _git_origin_with_credentials(job: Job) -> str:
    origin = job.repository.git_origin

    if is_set(job.repository.git_credentials):
        credentials = job.repository.git_credentials

        if origin.find('://') != -1 and origin.find('ssh://') == -1:
            # not ssh
            if origin.find('@') == -1 and \
                is_set(credentials.connect_user) and \
                    is_set(credentials.connect_pass):
                proto, origin_host = origin.split('://')
                origin = f'{proto}://{credentials.connect_user}:{credentials.connect_pass}@{origin_host}'

        else:
            # ssh
            if origin.find('@') == -1 and is_set(credentials.connect_user):
                origin = f'{credentials.connect_user}@{origin}'

    return origin


def _git_env(job: Job, path_run: Path) -> dict:
    env = {}
    if is_set(job.repository.git_credentials) and is_set(job.repository.git_credentials.ssh_key):
        path_run_repo = get_path_run_repo(path_run)
        path_run_repo.mkdir(mode=0o700)
        write_pwd_file(credentials=job.repository.git_credentials, attr='ssh_key', path_run=path_run_repo)
        env['GIT_SSH_COMMAND'] = f"ssh -i {get_pwd_file(path_run=path_run_repo, attr='ssh_key')}"

    return env


def _git_cmds_to_str(cmds: list[list[str]]) -> str:
    return '<br>'.join([' '.join(cmd) for cmd in cmds])


def create_repository(job: Job, execution: JobExecution, path_repo: Path, env: dict):
    if is_set(job.repository.git_override_initialize):
        execution.command_repository = job.repository.git_override_initialize.replace(',', '<br>')
        execution.save()
        _run_repo_config_cmds(
            cmds=job.repository.git_override_initialize,
            path_repo=path_repo,
            env=env,
            execution=execution,
        )
        return

    git_clone = ['git', 'clone', '--branch', job.repository.git_branch]

    if is_set(job.repository.git_limit_depth):
        git_clone.extend(['--depth', job.repository.git_limit_depth])

    git_clone.extend([_git_origin_with_credentials(job), str(path_repo)])

    git_cmds = [git_clone]

    if job.repository.git_lfs:
        git_cmds.append(['git', 'lfs', 'fetch'])
        git_cmds.append(['git', 'lfs', 'checkout'])

    # todo: fix db locked
    # execution.command_repository = _git_cmds_to_str(git_cmds)
    # execution.save()

    for cmd in git_cmds:
        print(cmd)
        _repo_process(cmd=cmd, path_repo=path_repo, env=env, execution=execution)


def update_repository(job: Job, execution: JobExecution, path_repo: Path, env: dict):
    if is_set(job.repository.git_override_update):
        execution.command_repository = job.repository.git_override_update.replace(',', '<br>')
        execution.save()
        _run_repo_config_cmds(
            cmds=job.repository.git_override_update,
            path_repo=path_repo,
            env=env,
            execution=execution,
        )
        return

    git_cmds = [
        ['git', 'reset', '--hard'],
        ['git', 'pull'],
    ]

    if job.repository.git_lfs:
        git_cmds.append(['git', 'lfs', 'fetch'])
        git_cmds.append(['git', 'lfs', 'checkout'])

    # todo: fix db locked
    # execution.command_repository = _git_cmds_to_str(git_cmds)
    # execution.save()

    for cmd in git_cmds:
        _repo_process(cmd=cmd, path_repo=path_repo, env=env, execution=execution)


def create_or_update_repository(job: Job, execution: JobExecution, path_run: Path):
    if is_null(job.repository) or job.repository.rtype_name == 'Static':
        return

    path_repo = get_path_repo(job=job, execution=execution)

    env = _git_env(job=job, path_run=path_run)

    _run_repo_config_cmds(
        cmds=job.repository.git_hook_pre,
        path_repo=path_repo,
        env=env,
        execution=execution,
    )

    if job.repository.git_isolate or not (Path(path_repo) / '.git/HEAD').is_file():
        create_repository(job=job, execution=execution, path_repo=path_repo, env=env)

    else:
        update_repository(job=job, execution=execution, path_repo=path_repo, env=env)

    _run_repo_config_cmds(
        cmds=job.repository.git_hook_post,
        path_repo=path_repo,
        env=env,
        execution=execution,
    )


def cleanup_repository(job: Job, execution: JobExecution, path_run: Path):
    if is_null(job.repository) or job.repository.rtype_name == 'Static':
        return

    path_run_repo = get_path_run_repo(path_run)
    for attr in BaseJobCredentials.SECRET_ATTRS:
        overwrite_and_delete_file(get_pwd_file(path_run=path_run_repo, attr=attr))

    if job.repository.git_isolate:
        rmtree(get_path_repo(job=job, execution=execution), ignore_errors=True)
