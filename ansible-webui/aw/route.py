from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import HttpResponse, redirect
from django.conf import settings

from aw.config.hardcoded import LOGIN_PATH
from aw.permission import authorized_to_exec, authorized_to_write


def _deny(request) -> (bool, HttpResponse):
    if request.method not in ['GET', 'POST', 'PUT']:
        return True, HttpResponse(status=405)

    return False, None


@login_required
def ui(request, **kwargs):
    bad, deny = _deny(request)
    if bad:
        return deny

    if request.method == 'POST':
        return ui_write(request)

    if request.method == 'PUT':
        return ui_exec(request)

    return HttpResponse(status=200, content=b"OK - read")


@login_required
@user_passes_test(authorized_to_write, login_url=LOGIN_PATH)
def ui_write(request, **kwargs):
    return HttpResponse(status=200, content=b"OK - write")


@login_required
@user_passes_test(authorized_to_exec, login_url=LOGIN_PATH)
def ui_exec(request, **kwargs):
    return HttpResponse(status=200, content=b"OK - exec")


def catchall(request, **kwargs):
    if request.user.is_authenticated:
        return redirect(settings.LOGIN_REDIRECT_URL)

    return redirect(LOGIN_PATH)
