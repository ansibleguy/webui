from django.db import models

from aw.model.base import BaseModel, DEFAULT_NONE, CHOICES_BOOL
from aw.model.job_credential import JobGlobalCredentials, JobUserCredentials


FIELD_TYPE_STR = 0
FIELD_TYPE_BOOL = 1
FIELD_TYPE_INT = 2

FIELD_TYPE_CHOICES = [
    (FIELD_TYPE_STR, 'String'),
    (FIELD_TYPE_BOOL, 'Boolean'),
    (FIELD_TYPE_INT, 'Integer'),
]

VAR_TYPE_EXTRA = 0
VAR_TYPE_ENV = 1

VAR_TYPE_CHOICES = [
    (VAR_TYPE_EXTRA, 'Extra-Var (Commandline Argument)'),
    (VAR_TYPE_ENV, 'Env-Var (Hidden)'),
]


class JobExecutionForm(BaseModel):
    name = models.CharField(max_length=200)
    credential_global = models.ForeignKey(
        JobGlobalCredentials, on_delete=models.SET_NULL, related_name='jobexecform_fk_credglob', null=True,
    )
    credential_user = models.ForeignKey(
        JobUserCredentials, on_delete=models.SET_NULL, related_name='jobexecform_fk_credusr', null=True,
    )


class JobExecutionFormField(BaseModel):
    form_fields = [
        'label', 'help', 'var', 'var_type', 'field_type', 'required', 'choices', 'multiple', 'separator',
        'validate_error', 'validate_regex', 'validate_max', 'validate_min',
    ]

    models.ForeignKey(JobExecutionForm, on_delete=models.CASCADE, related_name='jobexecformfield_fk_form')

    label = models.CharField(max_length=200, **DEFAULT_NONE)
    help = models.CharField(max_length=500, **DEFAULT_NONE)

    var = models.CharField(max_length=100)
    var_type = models.PositiveSmallIntegerField(choices=VAR_TYPE_CHOICES, default=VAR_TYPE_EXTRA)

    field_type = models.PositiveSmallIntegerField(choices=FIELD_TYPE_CHOICES, default=FIELD_TYPE_STR)
    required = models.BooleanField(choices=CHOICES_BOOL, default=False)
    choices = models.CharField(max_length=1000, **DEFAULT_NONE)
    multiple = models.BooleanField(choices=CHOICES_BOOL, default=False)
    separator = models.CharField(max_length=1, default=',', blank=True)

    validate_error = models.CharField(max_length=200, **DEFAULT_NONE)
    validate_regex = models.CharField(max_length=300, **DEFAULT_NONE)
    validate_max = models.PositiveSmallIntegerField(**DEFAULT_NONE)
    validate_min = models.PositiveSmallIntegerField(**DEFAULT_NONE)
