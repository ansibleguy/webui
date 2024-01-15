from os import environ

# pylint: disable=E0401
from django.urls import path, re_path
from django.conf.urls import include
from django.contrib import admin

from aw.route import ui, catchall
from aw.config.hardcoded import ENV_KEY_SERVE_STATIC
from aw.serve_static import urlpatterns_static
from aw.utils.deployment import deployment_dev

urlpatterns = []

if deployment_dev() or ENV_KEY_SERVE_STATIC not in environ:
    urlpatterns += urlpatterns_static

urlpatterns += [
    # auth
    path('a/', include('django.contrib.auth.urls')),  # login page
    path('m/', admin.site.urls),  # admin page

    # app
    path('ui/', ui),
    re_path(r'^ui/*', ui),

    # fallback
    re_path(r'^', catchall),
]
