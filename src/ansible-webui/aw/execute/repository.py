from pathlib import Path
from shutil import rmtree

from django.utils import timezone

from aw.config.main import config
from aw.model.job import Job, JobExecution
from aw.utils.util import is_null, is_set, write_file_0640
from aw.utils.subps import process
from aw.execute.play_credentials import write_pwd_file, get_pwd_file
from aw.execute.util import overwrite_and_delete_file, update_status, get_path_run, job_logs
from aw.model.job_credential import BaseJobCredentials
from aw.utils.handlers import AnsibleRepositoryError
from aw.model.repository import Repository
from aw.base import USERS


def repo_error(repository: Repository, msg: str):
    update_status(repository, status='Failed')
    raise AnsibleRepositoryError(msg).with_traceback(None) from None


def get_path_run_repo(path_run: Path) -> Path:
    return path_run / '.repository'


def get_path_repo_wo_isolate(repository: Repository) -> Path:
    if repository.rtype_name == 'Static':
        return repository.static_path

    path_repo = Path(config['path_run']) / 'repositories' / repository.name
    path_repo.mkdir(mode=0o750, parents=True, exist_ok=True)
    return path_repo


def get_path_repo(repository: Repository, execution: JobExecution) -> Path:
    path_repo = get_path_repo_wo_isolate(repository)

    if repository.git_isolate:
        path_repo = path_repo / execution.id
        path_repo.mkdir(mode=0o750, parents=True, exist_ok=True)

    return path_repo


def get_path_playbook_base(repository: Repository, execution: JobExecution) -> Path:
    path_repo = get_path_repo(repository=repository, execution=execution)
    if repository.rtype_name == 'Git' and is_set(repository.git_playbook_base):
        path_repo = path_repo / repository.git_playbook_base

    return path_repo


def get_project_dir(repository: Repository, execution: JobExecution) -> str:
    if is_null(repository):
        return config['path_play']

    return str(get_path_playbook_base(repository=repository, execution=execution))


def _repo_process(cmd: (str, list), path_repo: Path, env: dict, execution: JobExecution, repository: Repository):
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
        repo_error(
            repository=repository,
            msg=f"Repository command failed: '{cmd_str}'\n"
                f"Got error: '{result['stderr']}'\n"
                f"Got output: '{result['stdout']}'"
        )


def _run_repo_config_cmds(cmds: str, path_repo: Path, env: dict, execution: JobExecution, repository: Repository):
    if is_set(cmds):
        for cmd in cmds.split(','):
            _repo_process(
                cmd=cmd,
                path_repo=path_repo,
                env=env,
                execution=execution,
                repository=repository,
            )


def _git_origin_with_credentials(repository: Repository) -> str:
    origin = repository.git_origin

    if is_set(repository.git_credentials):
        credentials = repository.git_credentials

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


def _git_env(repository: Repository, path_run: Path) -> dict:
    env = {}
    if is_set(repository.git_credentials) and is_set(repository.git_credentials.ssh_key):
        path_run_repo = get_path_run_repo(path_run)
        path_run_repo.mkdir(mode=0o700, parents=True, exist_ok=True)
        write_pwd_file(credentials=repository.git_credentials, attr='ssh_key', path_run=path_run_repo)
        env['GIT_SSH_COMMAND'] = f"ssh -i {get_pwd_file(path_run=path_run_repo, attr='ssh_key')}"

    return env


def _git_cmds_to_str(cmds: list[list[str]]) -> str:
    return '<br>'.join([' '.join(cmd) for cmd in cmds])


def create_repository(repository: Repository, execution: JobExecution, path_repo: Path, env: dict):
    if is_set(repository.git_override_initialize):
        execution.command_repository = repository.git_override_initialize.replace(',', '<br>')
        execution.save()
        _run_repo_config_cmds(
            cmds=repository.git_override_initialize,
            path_repo=path_repo,
            env=env,
            execution=execution,
            repository=repository,
        )
        return

    git_clone = ['git', 'clone', '--branch', repository.git_branch]

    if is_set(repository.git_limit_depth):
        git_clone.extend(['--depth', repository.git_limit_depth])

    git_clone.extend([_git_origin_with_credentials(repository), str(path_repo)])

    git_cmds = [git_clone]

    if repository.git_lfs:
        git_cmds.append(['git', 'lfs', 'fetch'])
        git_cmds.append(['git', 'lfs', 'checkout'])

    # todo: fix db locked
    # execution.command_repository = _git_cmds_to_str(git_cmds)
    # execution.save()

    for cmd in git_cmds:
        _repo_process(
            cmd=cmd,
            path_repo=path_repo,
            env=env,
            execution=execution,
            repository=repository,
        )


def update_repository(repository: Repository, execution: JobExecution, path_repo: Path, env: dict):
    if is_set(repository.git_override_update):
        execution.command_repository = repository.git_override_update.replace(',', '<br>')
        execution.save()
        _run_repo_config_cmds(
            cmds=repository.git_override_update,
            path_repo=path_repo,
            env=env,
            execution=execution,
            repository=repository,
        )
        return

    git_cmds = [
        ['git', 'reset', '--hard'],
        ['git', 'pull'],
    ]

    if repository.git_lfs:
        git_cmds.append(['git', 'lfs', 'fetch'])
        git_cmds.append(['git', 'lfs', 'checkout'])

    # todo: fix db locked
    # execution.command_repository = _git_cmds_to_str(git_cmds)
    # execution.save()

    for cmd in git_cmds:
        _repo_process(
            cmd=cmd,
            path_repo=path_repo,
            env=env,
            execution=execution,
            repository=repository,
        )


def create_or_update_repository(repository: Repository, execution: JobExecution, path_run: Path):
    if is_null(repository) or repository.rtype_name == 'Static':
        return

    update_status(repository, status='Running')
    path_repo = get_path_repo(repository=repository, execution=execution)

    env = _git_env(repository=repository, path_run=path_run)

    _run_repo_config_cmds(
        cmds=repository.git_hook_pre,
        path_repo=path_repo,
        env=env,
        execution=execution,
        repository=repository,
    )

    if repository.git_isolate or not (Path(path_repo) / '.git/HEAD').is_file():
        create_repository(repository=repository, execution=execution, path_repo=path_repo, env=env)

    else:
        update_repository(repository=repository, execution=execution, path_repo=path_repo, env=env)

    repository.time_update = timezone.now()

    _run_repo_config_cmds(
        cmds=repository.git_hook_post,
        path_repo=path_repo,
        env=env,
        execution=execution,
        repository=repository,
    )

    update_status(repository, status='Finished')


def cleanup_repository(repository: Repository, execution: JobExecution, path_run: Path):
    if is_null(repository) or repository.rtype_name == 'Static':
        return

    path_run_repo = get_path_run_repo(path_run)
    for attr in BaseJobCredentials.SECRET_ATTRS:
        overwrite_and_delete_file(get_pwd_file(path_run=path_run_repo, attr=attr))

    if repository.git_isolate:
        rmtree(get_path_repo(repository=repository, execution=execution), ignore_errors=True)


def api_update_repository(repository: Repository, user: USERS):
    if is_null(repository) or repository.rtype_name == 'Static' or repository.git_isolate:
        return

    job = Job(name='')
    execution = JobExecution(user=user, job=job, comment='Manual Repository Update')
    job_logs(job=job, execution=execution)

    create_or_update_repository(repository=repository, execution=execution, path_run=get_path_run())
