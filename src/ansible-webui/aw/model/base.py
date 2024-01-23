from django.db import models
from django.utils import timezone

CHOICES_BOOL = (
    (True, 'Yes'),
    (False, 'No')
)


class BareModel(models.Model):
    created = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True


class BaseModel(BareModel):
    updated = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True
