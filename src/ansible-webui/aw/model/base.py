from django.db import models

CHOICES_BOOL = (
    (True, 'Yes'),
    (False, 'No')
)
DEFAULT_NONE = {'null': True, 'default': None, 'blank': True}
CHOICES_JOB_EXEC_STATUS = [
    (0, 'Waiting'),
    (1, 'Starting'),
    (2, 'Running'),
    (3, 'Failed'),
    (4, 'Finished'),
    (5, 'Stopping'),
    (6, 'Stopped'),
]


class BareModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class BaseModel(BareModel):
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
