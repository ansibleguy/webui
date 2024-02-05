from django.conf import settings
from rest_framework import serializers

from aw.model.job import Job
from aw.utils.permission import get_viewable_jobs


class JobReadResponse(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = Job.api_fields_read


def get_viewable_jobs_serialized(user: settings.AUTH_USER_MODEL) -> list[dict]:
    return [JobReadResponse(instance=job).data for job in get_viewable_jobs(user)]
