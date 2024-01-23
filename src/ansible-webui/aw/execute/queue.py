from aw.model.job import Job, JobQueue
from aw.utils.debug import log


def queue_get() -> (Job, None):
    # pylint: disable=E1101
    next_queue_item = JobQueue.objects.order_by('-created').first()
    if next_queue_item is None:
        return None

    next_job = next_queue_item.job
    next_queue_item.delete()
    return next_job


def queue_add(job: Job):
    log(msg=f"Job '{job.name}' added to execution queue", level=4)
    queue_item = JobQueue(job=job)
    queue_item.save()
