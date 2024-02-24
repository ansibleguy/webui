from aw.model.job import Job
from aw.model.job_credential import JobGlobalCredentials
from aw.base import USERS, GROUPS
from aw.model.repository import Repository


def choices_job() -> list[tuple]:
    # todo: only show jobs the user is privileged to view => get_viewable_jobs(user)
    return [(job.id, job.name) for job in Job.objects.all()]


def choices_global_credentials() -> list[tuple]:
    # todo: only show credentials the user is privileged to view => get_viewable_credentials(user)
    return [(credentials.id, credentials.name) for credentials in JobGlobalCredentials.objects.all()]


def choices_repositories() -> list[tuple]:
    # todo: only show credentials the user is privileged to view => get_viewable_credentials(user)
    return [(repo.id, repo.name) for repo in Repository.objects.all()]


def choices_user() -> list[tuple]:
    return [(user.id, user.username) for user in USERS.objects.all()]


def choices_group() -> list[tuple]:
    return [(group.id, group.name) for group in GROUPS.objects.all()]
