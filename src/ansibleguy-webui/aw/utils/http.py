from typing import Callable

from django.shortcuts import HttpResponse, redirect

from aw.config.hardcoded import LOGIN_PATH


def deny_request(request) -> (bool, HttpResponse):
    if request.method not in ['GET', 'POST', 'PUT']:
        return True, HttpResponse(status=405)

    return False, None


def ui_endpoint_wrapper(func) -> Callable:
    def wrapper(request, *args, **kwargs):
        del args
        del kwargs

        bad, deny = deny_request(request)
        if bad:
            return deny

        if not request.user.is_authenticated:
            return redirect(LOGIN_PATH)

        return func(request)

    return wrapper


def ui_endpoint_wrapper_kwargs(func) -> Callable:
    def wrapper(request, *args, **kwargs):
        del args

        bad, deny = deny_request(request)
        if bad:
            return deny

        if not request.user.is_authenticated:
            return redirect(LOGIN_PATH)

        return func(request, **kwargs)

    return wrapper
