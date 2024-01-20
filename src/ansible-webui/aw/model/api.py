from django.db import models
from django.conf import settings
from rest_framework_api_key.models import AbstractAPIKey


class AwAPIKey(AbstractAPIKey):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, editable=False)
