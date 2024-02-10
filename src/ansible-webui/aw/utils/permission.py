from django.conf import settings

from aw.model.job import Job, JobPermissionMapping, JobPermissionMemberUser, JobPermissionMemberGroup, \
    CHOICE_JOB_PERMISSION_READ, CHOICES_JOB_PERMISSION
from aw.utils.util import get_choice_by_value


def get_job_if_allowed(user: settings.AUTH_USER_MODEL, job: Job, permission_needed: int) -> (Job, None):
    # pylint: disable=E1101
    if job is None:
        return None

    if not isinstance(job, Job):
        raise ValueError(f"Provided job is invalid: '{job}'")

    if has_job_permission(user=user, job=job, permission_needed=permission_needed):
        return job

    return None


def has_job_permission(user: settings.AUTH_USER_MODEL, job: Job, permission_needed: int) -> bool:
    # pylint: disable=E1101
    if user.is_superuser:
        return True

    # if job has no permissions set
    permission_links = JobPermissionMapping.objects.filter(job=job)
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
        groups = JobPermissionMemberGroup.objects.filter(permission=link.permission)
        if groups.exists() and user.groups.filter(name__in=[
            group.name for group in groups
        ]).exists():
            return True

    return False


def get_viewable_jobs(user: settings.AUTH_USER_MODEL) -> list[Job]:
    # pylint: disable=E1101
    jobs = Job.objects.all()
    jobs_viewable = []

    for job in jobs:
        job = get_job_if_allowed(user=user, job=job, permission_needed=CHOICE_JOB_PERMISSION_READ)
        if job is not None:
            jobs_viewable.append(job)

    return jobs_viewable


def get_permission_name(perm: int) -> str:
    return get_choice_by_value(choices=CHOICES_JOB_PERMISSION, value=perm)
