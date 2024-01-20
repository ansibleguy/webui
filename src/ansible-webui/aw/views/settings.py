from django.urls import path
from django.shortcuts import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from aw.utils.http import ui_endpoint_wrapper
from aw.model.api import AwAPIKey


@login_required
@ui_endpoint_wrapper
def setting_api_key(request) -> HttpResponse:
    api_key_tokens = [key.name for key in AwAPIKey.objects.filter(user=request.user)]
    return render(
        request, status=200, template_name='settings/api_key.html',
        context={'api_key_tokens': api_key_tokens}
    )


urlpatterns_settings = [
    path('ui/settings/api_keys', setting_api_key),
]
