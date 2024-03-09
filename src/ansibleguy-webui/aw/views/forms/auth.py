from urllib.parse import urljoin

from django.shortcuts import redirect, render, HttpResponse
from django_saml2_auth.user import create_jwt_token

from aw.utils.http import ui_endpoint_wrapper_auth
from aw.settings import SAML2_AUTH, LOGIN_PATH, LOGIN_REDIRECT_URL


# SP-initiated SAML SSO; see: https://github.com/grafana/django-saml2-auth/issues/105
@ui_endpoint_wrapper_auth
def saml_sp_initiated_login(request) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect(LOGIN_REDIRECT_URL)

    return render(request, status=200, template_name='registration/saml.html')


@ui_endpoint_wrapper_auth
def saml_sp_initiated_login_init(request) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect(LOGIN_REDIRECT_URL)

    if request.method != 'POST' or 'username' not in request.POST:
        return redirect(f"{LOGIN_PATH}?error=Required 'username' was not provided!")

    token = create_jwt_token(request.POST['username'])
    assertion_url = SAML2_AUTH['ASSERTION_URL']
    sso_init_url = urljoin(assertion_url, f'a/saml/sp/?token={token}')
    return redirect(sso_init_url)
