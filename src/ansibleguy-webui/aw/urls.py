# pylint: disable=E0401
from django.urls import path, re_path
from django.conf.urls import include
from django.contrib import admin
from django.contrib.auth.views import LoginView, PasswordChangeView

from web_serve_static import urlpatterns_static
from aw.api import urlpatterns_api
from aw.views.main import urlpatterns_ui, catchall, logout
from aw.config.environment import check_aw_env_var_true, auth_mode_saml
from aw.utils.deployment import deployment_dev
from aw.views.forms.auth import saml_sp_initiated_login, saml_sp_initiated_login_init

urlpatterns = []

if deployment_dev() or check_aw_env_var_true(var='serve_static', fallback=True):
    urlpatterns += urlpatterns_static

urlpatterns += urlpatterns_api

# AUTH
if auth_mode_saml():
    urlpatterns += [
        path('a/saml/init/', saml_sp_initiated_login_init),
        path('a/saml/', include('django_saml2_auth.urls')),
        # user views
        path('a/login/', saml_sp_initiated_login, name='login_sso'),
        path('a/login/fallback/', LoginView.as_view(), name='login'),
    ]

else:
    urlpatterns += [
        path('a/login/', LoginView.as_view(), name='login'),
    ]

urlpatterns += [
    path('a/password_change/', PasswordChangeView.as_view()),
    path('_admin/', admin.site.urls),
    path('o/', logout),
]

# UI
urlpatterns += urlpatterns_ui
urlpatterns += [
    # fallback
    re_path(r'^', catchall),
]
