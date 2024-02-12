from django.db import models
from rest_framework_api_key.models import AbstractAPIKey

from aw.base import USERS


class AwAPIKey(AbstractAPIKey):
    user = models.ForeignKey(USERS, on_delete=models.CASCADE, editable=False)
