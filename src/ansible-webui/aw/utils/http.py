from typing import Callable

from django.shortcuts import HttpResponse


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

        return func(request)

    return wrapper
