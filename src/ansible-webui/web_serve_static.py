"""
used to serve static files if no proxy is in use
source: django.contrib.staticfiles.views(serve)

can be switched off by setting the environmental variable 'AW_STATIC'
"""
from posixpath import normpath
from os import path as os_path
from re import escape as regex_escape

from django.contrib.staticfiles import finders
from django.http import Http404
from django.views import static
from django.conf import settings
from django.urls import re_path


def serve(request, path, **kwargs):
    normalized_path = normpath(path).lstrip('/')
    absolute_path = finders.find(normalized_path)

    if not absolute_path:
        if path.endswith("/") or path == "":
            raise Http404('Directory indexes are not allowed here.')
        raise Http404(f"'{path}' could not be found")

    document_root, path = os_path.split(absolute_path)
    return static.serve(request, path, document_root=document_root, **kwargs)


# pylint: disable=C0209
urlpatterns_static = [re_path(
    r"^%s(?P<path>.*)$" % regex_escape(settings.STATIC_URL.lstrip('/')), serve,
)]
