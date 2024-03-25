from django.db import models

from aw.model.base import BaseModel, BareModel, CHOICES_BOOL
from aw.model.job import Job

from aw.base import USERS, GROUPS

ALERT_TYPE_EMAIL = 0
ALERT_TYPE_PLUGIN = 1

ALERT_TYPE_CHOICES = [
    (ALERT_TYPE_EMAIL, 'E-Mail'),
    (ALERT_TYPE_PLUGIN, 'Plugin'),
]

ALERT_CONDITION_FAIL = 0
ALERT_CONDITION_SUCCESS = 1
ALERT_CONDITION_ALWAYS = 2

ALERT_CONDITION_CHOICES = [
    (ALERT_CONDITION_FAIL, 'Failure'),
    (ALERT_CONDITION_SUCCESS, 'Success'),
    (ALERT_CONDITION_ALWAYS, 'Always'),
]


class AlertPlugin(BaseModel):
    name = models.CharField(max_length=100)
    executable = models.CharField(max_length=300)


class BaseAlert(BaseModel):
    name = models.CharField(max_length=100)
    alert_type = models.PositiveSmallIntegerField(choices=ALERT_TYPE_CHOICES, default=ALERT_TYPE_EMAIL)
    plugin = models.ForeignKey(
        AlertPlugin, on_delete=models.CASCADE, null=True, related_name='alert_fk_plugin',
    )
    jobs_all = models.BooleanField(choices=CHOICES_BOOL, default=False)
    jobs = models.ManyToManyField(
        Job,
        through='AlertJobMapping',
        through_fields=('alert', 'job'),
    )
    condition = models.PositiveSmallIntegerField(choices=ALERT_CONDITION_CHOICES, default=ALERT_CONDITION_FAIL)

    class Meta:
        abstract = True


class AlertGlobal(BaseAlert):
    def __str__(self) -> str:
        return f"Global Alert '{self.name}'"


class AlertGroup(BaseAlert):
    group = models.ForeignKey(
        GROUPS, on_delete=models.SET_NULL, null=True, related_name='alert_fk_group',
    )

    def __str__(self) -> str:
        return f"Alert '{self.name}' of group '{self.group.name}'"


class AlertUser(BaseAlert):
    user = models.ForeignKey(
        USERS, on_delete=models.SET_NULL, null=True, related_name='alert_fk_user', editable=False,
    )

    def __str__(self) -> str:
        return f"Alert '{self.name}' of user '{self.user.username}'"


class AlertUserJobMapping(BareModel):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    alert = models.ForeignKey(AlertUser, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.alert} linked to job '{self.job.name}'"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['job', 'alert'], name='alertjobmmap_unique')
        ]
