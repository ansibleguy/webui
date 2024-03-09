# pylint: disable=E0401
from django.urls import path, re_path
from django.conf.urls import include
from django.contrib import admin
from django.contrib.auth import views as auth_views


from web_serve_static import urlpatterns_static
from aw.api import urlpatterns_api
from aw.views.main import urlpatterns_ui, catchall, logout
from aw.config.environment import check_aw_env_var_true
from aw.utils.deployment import deployment_dev
from aw.config.environment import auth_mode_saml

urlpatterns = []

if deployment_dev() or check_aw_env_var_true(var='serve_static', fallback=True):
    urlpatterns += urlpatterns_static

urlpatterns += urlpatterns_api

if auth_mode_saml():
    from django_saml2_auth import views as saml_auth_views
    urlpatterns += [
        re_path(r'^a/saml/', include('django_saml2_auth.urls')),
        re_path(r'^a/sso/$', saml_auth_views.signin),
        re_path(r'^o/$', saml_auth_views.signout),
    ]

else:
    urlpatterns += [
        re_path(r'^o/$', logout),
    ]

urlpatterns += [
    # auth
    path('a/', include('django.contrib.auth.urls')),  # login page
    path('a/password_change/', auth_views.PasswordChangeView.as_view()),
    path('_admin/', admin.site.urls),  # admin page
    path('o/', logout),
]

urlpatterns += urlpatterns_ui
urlpatterns += [
    # fallback
    re_path(r'^', catchall),
]
