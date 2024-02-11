from django.contrib.auth.models import User, Group

from aw.model.job import Job
from aw.model.job_credential import JobGlobalCredentials


def choices_job() -> list[tuple]:
    # pylint: disable=E1101
    return [(job.id, job.name) for job in Job.objects.all()]


def choices_credentials() -> list[tuple]:
    # pylint: disable=E1101
    return [(credentials.id, credentials.name) for credentials in JobGlobalCredentials.objects.all()]


def choices_user() -> list[tuple]:
    return [(user.id, user.username) for user in User.objects.all()]


def choices_group() -> list[tuple]:
    return [(group.id, group.name) for group in Group.objects.all()]
