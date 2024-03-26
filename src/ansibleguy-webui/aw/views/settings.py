from django.urls import path
from django.shortcuts import HttpResponse, render
from django.contrib.auth.decorators import login_required

from aw.utils.http import ui_endpoint_wrapper
from aw.views.forms.settings import setting_permission_edit, setting_alert_plugin_edit, setting_alert_user_edit, \
    setting_alert_global_edit, setting_alert_group_edit


@login_required
@ui_endpoint_wrapper
def setting_api_key(request) -> HttpResponse:
    return render(request, status=200, template_name='settings/api_key.html', context={'show_update_time': True})


@login_required
@ui_endpoint_wrapper
def setting_permission(request) -> HttpResponse:
    return render(request, status=200, template_name='settings/permission.html', context={'show_update_time': True})


@login_required
@ui_endpoint_wrapper
def setting_alert(request) -> HttpResponse:
    return render(request, status=200, template_name='settings/alert.html', context={'show_update_time': True})


urlpatterns_settings = [
    path('ui/settings/api_keys', setting_api_key),
    path('ui/settings/permissions/<int:perm_id>', setting_permission_edit),
    path('ui/settings/permissions', setting_permission),
    path('ui/settings/alerts/plugin/<int:plugin_id>', setting_alert_plugin_edit),
    path('ui/settings/alerts/user/<int:alert_id>', setting_alert_user_edit),
    path('ui/settings/alerts/group/<int:alert_id>', setting_alert_group_edit),
    path('ui/settings/alerts/global/<int:alert_id>', setting_alert_global_edit),
    path('ui/settings/alerts', setting_alert),
]
