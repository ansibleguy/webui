from urllib.parse import urljoin
from datetime import datetime, timedelta, timezone

from django.shortcuts import redirect, render, HttpResponse
from django_saml2_auth.user import create_jwt_token
from jwt import encode as jwt_encode

from aw.utils.http import ui_endpoint_wrapper_auth
from aw.settings import SAML2_AUTH, LOGIN_PATH, LOGIN_REDIRECT_URL
from aw.base import USERS


# SP-initiated SAML SSO; see: https://github.com/grafana/django-saml2-auth/issues/105
def __create_jwt_token(user_id: str) -> str:
    # stripped-down copy of django_saml2_auth.user.create_jwt_token
    if SAML2_AUTH['JWT_ALGORITHM'] != 'none':
        return create_jwt_token(user_id)

    payload = {
        USERS.USERNAME_FIELD: user_id,
        'exp': (datetime.now(tz=timezone.utc) +
                timedelta(seconds=SAML2_AUTH['JWT_EXP'])).timestamp()
    }
    return jwt_encode(payload, secret=None, algorithm='none')


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

    token = __create_jwt_token(request.POST['username'])
    assertion_url = SAML2_AUTH['ASSERTION_URL']
    sso_init_url = urljoin(assertion_url, f'a/saml/sp/?token={token}')
    return redirect(sso_init_url)
