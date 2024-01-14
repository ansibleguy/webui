from django.db import models

BOOLEAN_CHOICES = (
    (True, 'Yes'),
    (False, 'No')
)


class BareModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


