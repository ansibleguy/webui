from django.shortcuts import HttpResponse


def deny_request(request) -> (bool, HttpResponse):
    if request.method not in ['GET', 'POST', 'PUT']:
        return True, HttpResponse(status=405)

    return False, None
