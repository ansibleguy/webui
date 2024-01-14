# pylint: disable=E0401
from django.urls import path, re_path
from django.conf.urls import include
from django.contrib import admin

from aw.route import ui, catchall

urlpatterns = [
    # auth
    path('accounts/', include('django.contrib.auth.urls')),  # login page
    path('admin/', admin.site.urls),  # admin page

    # app
    re_path(r'^ui/*', ui),

    # fallback
    re_path(r'^', catchall),
]
