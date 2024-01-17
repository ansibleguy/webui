from os import environ

# pylint: disable=E0401
from django.urls import path, re_path
from django.conf.urls import include
from django.contrib import admin

from base.serve_static import urlpatterns_static
from aw.route import ui, catchall, logout, not_implemented, manage
from aw.config.hardcoded import ENV_KEY_SERVE_STATIC
from aw.utils.deployment import deployment_dev

urlpatterns = []

if deployment_dev() or ENV_KEY_SERVE_STATIC not in environ:
    urlpatterns += urlpatterns_static

urlpatterns += [
    # auth
    path('a/', include('django.contrib.auth.urls')),  # login page
    path('m/', admin.site.urls),  # admin page
    path('o/', logout),

    # app
    path('ui/', ui),
    path('ui/m/', manage),
    path('ui/job/', not_implemented),
    path('ui/settings/', not_implemented),
    re_path(r'^ui/*', ui),

    # fallback
    re_path(r'^', catchall),
]
