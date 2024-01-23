from django.conf import settings

from aw.model.job import Job, JobQueue
from aw.utils.debug import log


def queue_get() -> (tuple[Job, settings.AUTH_USER_MODEL], None):
    # pylint: disable=E1101
    next_queue_item = JobQueue.objects.order_by('-created').first()
    if next_queue_item is None:
        return None

    job, user = next_queue_item.job, next_queue_item.user
    next_queue_item.delete()
    return job, user


def queue_add(job: Job, user: settings.AUTH_USER_MODEL):
    log(msg=f"Job '{job.name}' added to execution queue", level=4)
    queue_item = JobQueue(job=job, user=user)
    queue_item.save()
