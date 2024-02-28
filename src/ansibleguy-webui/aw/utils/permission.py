from aw.model.job import Job
from aw.model.permission import JobPermissionMapping, JobPermissionMemberUser, JobPermissionMemberGroup, \
    CHOICE_PERMISSION_READ, JobCredentialsPermissionMapping, JobRepositoryPermissionMapping, JobPermission, \
    CHOICE_PERMISSION_WRITE, CHOICE_PERMISSION_DELETE
from aw.model.job_credential import BaseJobCredentials, JobGlobalCredentials
from aw.model.repository import Repository
from aw.base import USERS
from aw.utils.debug import log
from aw.config.hardcoded import GRP_MANAGER


def get_job_if_allowed(user: USERS, job: Job, permission_needed: int) -> (Job, None):
    if job is None:
        return None

    if not isinstance(job, Job):
        raise ValueError(f"Provided job is invalid: '{job}'")

    if has_job_permission(user=user, job=job, permission_needed=permission_needed):
        return job

    return None


def _evaluate_permission(permission: JobPermission, user: USERS, permission_needed: int) -> bool:
    # ignore permission if access-level is too low
    if permission.permission < permission_needed:
        return False

    # if one of the permissions allows the user
    if JobPermissionMemberUser.objects.filter(user=user, permission=permission).exists():
        return True

    # if one of the permissions allows a group that the user is a member of
    links = JobPermissionMemberGroup.objects.filter(permission=permission)
    if links.exists() and user.groups.filter(name__in=[
        link.group.name for link in links
    ]).exists():
        return True

    return False


def _has_permission(
        permission_links: (JobPermissionMapping, JobCredentialsPermissionMapping), permission_needed: int,
        user: USERS, permission_attr_all: str, manager: str = None,
) -> bool:
    if user.is_superuser:
        return True

    if manager is not None and \
            permission_needed in [CHOICE_PERMISSION_READ, CHOICE_PERMISSION_WRITE, CHOICE_PERMISSION_DELETE] and \
            has_manager_privileges(user=user, kind=manager):
        return True

    # 'all' permissions
    for permission in JobPermission.objects.filter(**{permission_attr_all: True}):
        if _evaluate_permission(permission=permission, user=user, permission_needed=permission_needed):
            log(
                msg=f"User '{user}' privileged ({permission_needed}) through permission {permission.name}",
                level=7,
            )
            return True

    # lined permissions
    for link in permission_links:
        if _evaluate_permission(permission=link.permission, user=user, permission_needed=permission_needed):
            log(
                msg=f"User '{user}' privileged ({permission_needed}) through permission {link.permission.name}",
                level=7,
            )
            return True

    return False


def has_job_permission(user: USERS, job: Job, permission_needed: int) -> bool:
    return _has_permission(
        permission_links=JobPermissionMapping.objects.filter(job=job),
        permission_needed=permission_needed,
        permission_attr_all='jobs_all',
        user=user,
        manager='job',
    )


def has_credentials_permission(
        user: USERS, credentials: BaseJobCredentials, permission_needed: int,
) -> bool:
    return _has_permission(
        permission_links=JobCredentialsPermissionMapping.objects.filter(credentials=credentials),
        permission_needed=permission_needed,
        permission_attr_all='credentials_all',
        user=user,
        manager='credentials',
    )


def has_repository_permission(
        user: USERS, repository: Repository, permission_needed: int,
) -> bool:
    return _has_permission(
        permission_links=JobRepositoryPermissionMapping.objects.filter(repository=repository),
        permission_needed=permission_needed,
        permission_attr_all='repositories_all',
        user=user,
        manager='repository',
    )


def get_viewable_jobs(user: USERS) -> list[Job]:
    jobs_viewable = []

    for job in Job.objects.all():
        if has_job_permission(user=user, job=job, permission_needed=CHOICE_PERMISSION_READ):
            jobs_viewable.append(job)

    return jobs_viewable


def get_viewable_credentials(user: USERS) -> list[BaseJobCredentials]:
    credentials_viewable = []

    for credentials in JobGlobalCredentials.objects.all():
        if has_credentials_permission(user=user, credentials=credentials, permission_needed=CHOICE_PERMISSION_READ):
            credentials_viewable.append(credentials)

    return credentials_viewable


def get_viewable_repositories(user: USERS) -> list[Repository]:
    repositories_viewable = []

    for repository in Repository.objects.all():
        if has_repository_permission(user=user, repository=repository, permission_needed=CHOICE_PERMISSION_READ):
            repositories_viewable.append(repository)

    return repositories_viewable


def has_manager_privileges(user: USERS, kind: str) -> bool:
    if user.is_superuser:
        return True

    return user.groups.filter(name=GRP_MANAGER[kind]).exists()
