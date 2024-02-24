from aw.model.job import Job, JobQueue
from aw.utils.debug import log
from aw.base import USERS


def queue_get() -> (tuple[Job, USERS], None):
    next_queue_item = JobQueue.objects.order_by('-created').first()
    if next_queue_item is None:
        return None

    job, user = next_queue_item.job, next_queue_item.user
    next_queue_item.delete()
    return job, user


def queue_add(job: Job, user: USERS):
    log(msg=f"Job '{job.name}' added to execution queue", level=4)
    JobQueue(job=job, user=user).save()
