from django.db import models

CHOICES_BOOL = (
    (True, 'Yes'),
    (False, 'No')
)


class BareModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class BaseModel(BareModel):
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
