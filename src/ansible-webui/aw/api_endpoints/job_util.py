from django.conf import settings
from rest_framework import serializers

from aw.model.job import Job, JobPermissionMapping, JobPermissionMemberUser, JobPermissionMemberGroup, \
    CHOICE_JOB_PERMISSION_READ


class JobReadResponse(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = Job.api_fields


def get_job_if_allowed(user: settings.AUTH_USER_MODEL, job: Job, permission_needed: int) -> (Job, None):
    # pylint: disable=E1101
    if job is None:
        return None

    if not isinstance(job, Job):
        raise ValueError(f"Provided job is invalid: '{job}'")

    # if job has no permissions set
    permission_links = JobPermissionMapping.objects.filter(job=job)
    if not permission_links.exists():
        return job

    for link in permission_links:
        # ignore permission if access-level is too low
        if link.permission < permission_needed:
            continue

        # if one of the permissions allows the user
        if JobPermissionMemberUser.objects.filter(user=user, permission=link.permission).exists():
            return job

        # if one of the permissions allows a group that the user is a member of
        groups = JobPermissionMemberGroup.objects.filter(permission=link.permission)
        if groups.exists() and user.groups.filter(name__in=[
            group.name for group in groups
        ]).exists():
            return job

    return None


def job_action_allowed(user: settings.AUTH_USER_MODEL, job: Job, permission_needed: int) -> bool:
    return get_job_if_allowed(user=user, job=job, permission_needed=permission_needed) is not None


def get_viewable_jobs(user: settings.AUTH_USER_MODEL) -> list[Job]:
    # pylint: disable=E1101
    jobs = Job.objects.all()
    jobs_viewable = []

    for job in jobs:
        job = get_job_if_allowed(user=user, job=job, permission_needed=CHOICE_JOB_PERMISSION_READ)
        if job is not None:
            jobs_viewable.append(job)

    return jobs_viewable


def get_viewable_jobs_serialized(user: settings.AUTH_USER_MODEL) -> list[dict]:
    return [JobReadResponse(instance=job).data for job in get_viewable_jobs(user)]
