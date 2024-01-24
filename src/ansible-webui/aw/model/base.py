from django.db import models
from django.utils import timezone

CHOICES_BOOL = (
    (True, 'Yes'),
    (False, 'No')
)
DEFAULT_NONE = {'null': True, 'default': None, 'blank': True}


class BareModel(models.Model):
    created = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True


class BaseModel(BareModel):
    updated = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True
