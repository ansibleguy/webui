from django import template

from aw.config.main import VERSION
from aw.config.navigation import NAVIGATION


register = template.Library()


@register.simple_tag
def get_version() -> str:
    return VERSION


@register.simple_tag
def set_var(val):
    return val


@register.filter
def get_full_uri(request):
    return request.build_absolute_uri()


@register.filter
def get_nav(key: str) -> dict:
    # serves navigation config to template
    return NAVIGATION[key]


@register.filter
def get_type(value):
    return str(type(value)).replace("<class '", '').replace("'>", '')
