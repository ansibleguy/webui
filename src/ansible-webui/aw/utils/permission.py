from aw.model.job import Job
from aw.model.job_permission import JobPermissionMapping, JobPermissionMemberUser, JobPermissionMemberGroup, \
    CHOICE_PERMISSION_READ, CHOICES_PERMISSION, JobCredentialsPermissionMapping
from aw.model.job_credential import BaseJobCredentials, JobGlobalCredentials, JobUserCredentials
from aw.utils.util import get_choice_by_value
from aw.base import USERS


def get_job_if_allowed(user: USERS, job: Job, permission_needed: int) -> (Job, None):
    if job is None:
        return None

    if not isinstance(job, Job):
        raise ValueError(f"Provided job is invalid: '{job}'")

    if has_job_permission(user=user, job=job, permission_needed=permission_needed):
        return job

    return None


def _has_permission(
        permission_links: (JobPermissionMapping, JobCredentialsPermissionMapping), permission_needed: int,
        user: USERS,
) -> bool:
    if user.is_superuser:
        return True

    if not permission_links.exists():
        return True

    for link in permission_links:
        # ignore permission if access-level is too low
        if link.permission.permission < permission_needed:
            continue

        # if one of the permissions allows the user
        if JobPermissionMemberUser.objects.filter(user=user, permission=link.permission).exists():
            return True

        # if one of the permissions allows a group that the user is a member of
        links = JobPermissionMemberGroup.objects.filter(permission=link.permission)
        if links.exists() and user.groups.filter(name__in=[
            link.group.name for link in links
        ]).exists():
            return True

    return False


def has_job_permission(user: USERS, job: Job, permission_needed: int) -> bool:
    return _has_permission(
        permission_links=JobPermissionMapping.objects.filter(job=job),
        permission_needed=permission_needed,
        user=user,
    )


def has_credentials_permission(
        user: USERS, credentials: BaseJobCredentials, permission_needed: int,
) -> bool:
    return _has_permission(
        permission_links=JobCredentialsPermissionMapping.objects.filter(credentials=credentials),
        permission_needed=permission_needed,
        user=user,
    )


def get_viewable_jobs(user: USERS) -> list[Job]:
    jobs_viewable = []

    for job in Job.objects.all():
        if has_job_permission(user=user, job=job, permission_needed=CHOICE_PERMISSION_READ):
            jobs_viewable.append(job)

    return jobs_viewable


def get_viewable_credentials(user: USERS) -> list[BaseJobCredentials]:
    credentials_viewable = JobUserCredentials.objects.filter(user=user)

    for credentials in JobGlobalCredentials.objects.all():
        if has_credentials_permission(user=user, credentials=credentials, permission_needed=CHOICE_PERMISSION_READ):
            credentials_viewable.append(credentials)

    return credentials_viewable


def get_permission_name(perm: int) -> str:
    return get_choice_by_value(choices=CHOICES_PERMISSION, value=perm)
