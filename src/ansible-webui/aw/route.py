from django.contrib.auth.decorators import login_required  # user_passes_test
from django.shortcuts import HttpResponse, redirect, render
from django.conf import settings
from django.contrib.auth.views import logout_then_login

from aw.config.hardcoded import LOGIN_PATH


def _deny(request) -> (bool, HttpResponse):
    if request.method not in ['GET', 'POST', 'PUT']:
        return True, HttpResponse(status=405)

    return False, None


@login_required
def ui(request, **kwargs):
    del kwargs
    bad, deny = _deny(request)
    if bad:
        return deny

    if request.method == 'POST':
        return ui_write(request)

    if request.method == 'PUT':
        return ui_exec(request)

    return render(request, status=200, template_name='fallback.html', context={'content': 'OK - read'})


# @user_passes_test(authorized_to_write, login_url=LOGIN_PATH)
@login_required
def ui_write(request, **kwargs):
    del kwargs
    return render(request, status=200, template_name='fallback.html', context={'content': 'OK - write'})


# @user_passes_test(authorized_to_exec, login_url=LOGIN_PATH)
@login_required
def ui_exec(request, **kwargs):
    del kwargs
    return render(request, status=200, template_name='fallback.html', context={'content': 'OK - exec'})


@login_required
def manage(request, **kwargs):
    del kwargs
    return render(request, status=200, template_name='fallback.html', context={
        'content': '<iframe width="100%" height="100%" marginheight="0" marginwidth="0" frameborder="0" '
                   'scrolling="auto" src="/m/" title="Manage"></iframe>'
    })


def not_implemented(request, **kwargs):
    del kwargs
    return render(request, status=404, template_name='fallback.html', context={'content': 'Not yet implemented'})


def catchall(request, **kwargs):
    del kwargs
    if request.user.is_authenticated:
        return redirect(settings.LOGIN_REDIRECT_URL)

    return redirect(LOGIN_PATH)


def logout(request, **kwargs):
    del kwargs
    return logout_then_login(request)
