from django.db import models

from aw.utils.util import get_choice_value_by_key
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
    form_fields = ['name', 'executable']
    api_fields = ['id']
    api_fields.extend(form_fields)

    name = models.CharField(max_length=100)
    executable = models.CharField(max_length=300)


class BaseAlert(BaseModel):
    form_fields = ['name', 'alert_type', 'plugin', 'jobs_all', 'jobs', 'condition']
    api_fields_write = ['id']
    api_fields_write.extend(form_fields)
    api_fields_read = ['alert_type_name', 'condition_name']
    api_fields_read.extend(api_fields_write)

    name = models.CharField(max_length=100)
    alert_type = models.PositiveSmallIntegerField(choices=ALERT_TYPE_CHOICES, default=ALERT_TYPE_EMAIL)
    jobs_all = models.BooleanField(choices=CHOICES_BOOL, default=False)
    condition = models.PositiveSmallIntegerField(choices=ALERT_CONDITION_CHOICES, default=ALERT_CONDITION_FAIL)

    @property
    def alert_type_name(self) -> str:
        return get_choice_value_by_key(choices=ALERT_TYPE_CHOICES, find=self.alert_type)

    @property
    def condition_name(self) -> str:
        return get_choice_value_by_key(choices=ALERT_CONDITION_CHOICES, find=self.condition)

    class Meta:
        abstract = True


class AlertGlobal(BaseAlert):
    plugin = models.ForeignKey(
        AlertPlugin, on_delete=models.CASCADE, null=True, related_name='alertglob_fk_plugin',
    )
    jobs = models.ManyToManyField(
        Job,
        through='AlertGlobalJobMapping',
        through_fields=('alert', 'job'),
    )

    @property
    def plugin_name(self) -> str:
        return self.plugin.name

    def __str__(self) -> str:
        return f"Global Alert '{self.name}'"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name'], name='alertglob_name_unique')
        ]


class AlertGlobalJobMapping(BareModel):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    alert = models.ForeignKey(AlertGlobal, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.alert} linked to job '{self.job.name}'"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['job', 'alert'], name='alertglobjobmmap_unique')
        ]


class AlertGroup(BaseAlert):
    form_fields = BaseAlert.form_fields.copy()
    form_fields.extend(['group'])
    api_fields_write = BaseAlert.api_fields_write.copy()
    api_fields_write.extend(['group'])
    api_fields_read = BaseAlert.api_fields_read.copy()
    api_fields_read.extend(['group', 'group_name'])

    group = models.ForeignKey(
        GROUPS, on_delete=models.CASCADE, related_name='alertgrp_fk_group',
    )
    plugin = models.ForeignKey(
        AlertPlugin, on_delete=models.CASCADE, null=True, related_name='alertgrp_fk_plugin',
    )
    jobs = models.ManyToManyField(
        Job,
        through='AlertGroupJobMapping',
        through_fields=('alert', 'job'),
    )

    @property
    def plugin_name(self) -> str:
        return self.plugin.name

    @property
    def group_name(self) -> str:
        return self.group.name

    def __str__(self) -> str:
        return f"Alert '{self.name}' of group '{self.group.name}'"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name'], name='alertgrp_name_unique')
        ]


class AlertGroupJobMapping(BareModel):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    alert = models.ForeignKey(AlertGroup, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.alert} linked to job '{self.job.name}'"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['job', 'alert'], name='alertgrpjobmmap_unique')
        ]


class AlertUser(BaseAlert):
    api_fields_read = BaseAlert.api_fields_read.copy()
    api_fields_write = BaseAlert.api_fields_write.copy()
    api_fields_write.append('user')

    user = models.ForeignKey(
        USERS, on_delete=models.CASCADE, related_name='alertuser_fk_user', editable=False,
    )
    plugin = models.ForeignKey(
        AlertPlugin, on_delete=models.CASCADE, null=True, related_name='alertuser_fk_plugin',
    )
    jobs = models.ManyToManyField(
        Job,
        through='AlertUserJobMapping',
        through_fields=('alert', 'job'),
    )

    @property
    def plugin_name(self) -> str:
        return self.plugin.name

    def __str__(self) -> str:
        return f"Alert '{self.name}' of user '{self.user.username}'"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'user'], name='alertuser_name_unique')
        ]


class AlertUserJobMapping(BareModel):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    alert = models.ForeignKey(AlertUser, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.alert} linked to job '{self.job.name}'"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['job', 'alert'], name='alertuserjobmmap_unique')
        ]
