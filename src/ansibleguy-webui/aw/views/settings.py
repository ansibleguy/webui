from django.urls import path
from django.shortcuts import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from aw.utils.http import ui_endpoint_wrapper
from aw.views.forms.settings import setting_permission_edit


@login_required
@ui_endpoint_wrapper
def setting_api_key(request) -> HttpResponse:
    return render(request, status=200, template_name='settings/api_key.html', context={'show_update_time': True})


@login_required
@ui_endpoint_wrapper
def setting_permission(request) -> HttpResponse:
    return render(request, status=200, template_name='settings/permission.html', context={'show_update_time': True})


urlpatterns_settings = [
    path('ui/settings/api_keys', setting_api_key),
    path('ui/settings/permissions/<int:perm_id>', setting_permission_edit),
    path('ui/settings/permissions', setting_permission),
]
