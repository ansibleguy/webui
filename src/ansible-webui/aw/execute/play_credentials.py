from pathlib import Path

from django.core.exceptions import ObjectDoesNotExist

from aw.model.job import Job, JobExecution
from aw.model.job_credential import BaseJobCredentials, JobUserCredentials
from aw.utils.permission import has_credentials_permission, CHOICE_PERMISSION_READ
from aw.base import USERS
from aw.utils.debug import log  # log_warn
from aw.utils.util import is_set, is_null
from aw.execute.util import config_error, write_file_0600


def get_pwd_file(path_run: (str, Path), attr: str) -> str:
    return f"{path_run}/.aw_{attr}"


def get_pwd_file_arg(credentials: BaseJobCredentials, attr: str, path_run: (Path, str)) -> (str, None):
    if is_null(getattr(credentials, attr)):
        return None

    return f"--{BaseJobCredentials.SECRET_ATTRS_ARGS[attr]} {get_pwd_file(path_run=path_run, attr=attr)}"


def write_pwd_file(credentials: BaseJobCredentials, attr: str, path_run: (Path, str)):
    if credentials is None or is_null(getattr(credentials, attr)):
        return None

    return write_file_0600(
        file=get_pwd_file(path_run=path_run, attr=attr),
        content=getattr(credentials, attr),
    )


def _scheduled_or_has_credentials_access(user: USERS, credentials: BaseJobCredentials) -> bool:
    if user is None:
        # scheduled execution; permission has been checked at creation-time
        # todo: add 'owner' to jobs so we can re-check the permissions of scheduled jobs (?)
        return True

    permitted = has_credentials_permission(
        user=user,
        credentials=credentials,
        permission_needed=CHOICE_PERMISSION_READ,
    )
    if not permitted:
        log(
            msg=f"User '{user.username}' has no permission to use credentials {credentials.name}",
            level=7,
        )

    return permitted


def get_credentials_to_use(job: Job, execution: JobExecution) -> (BaseJobCredentials, None):
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


def commandline_arguments_credentials(credentials: BaseJobCredentials, path_run: Path) -> list:
    cmd_arguments = []

    for attr, flag in BaseJobCredentials.PUBLIC_ATTRS_ARGS.items():
        if is_set(getattr(credentials, attr)):
            cmd_arguments.append(f'{flag} {getattr(credentials, attr)}')

    for attr in BaseJobCredentials.SECRET_ATTRS:
        pwd_arg = get_pwd_file_arg(credentials, attr=attr, path_run=path_run)
        if pwd_arg is not None:
            cmd_arguments.append(pwd_arg)

    return cmd_arguments
