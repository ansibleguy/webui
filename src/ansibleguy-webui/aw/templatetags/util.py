from functools import cache

from django import template

from aw.config.main import config
from aw.settings import STATIC_URL
from aw.config.navigation import NAVIGATION
from aw.utils.version import get_version as get_version_util

register = template.Library()


@register.simple_tag
def get_version() -> str:
    return get_version_util()


@register.simple_tag
def get_logo() -> str:
    url = config['logo_url']
    if not url.startswith('http'):
        return f"{STATIC_URL}{url}"

    return config['logo_url']


@register.simple_tag
def set_var(val):
    return val


@register.filter
def get_full_uri(request):
    return request.build_absolute_uri()


@cache
@register.filter
def get_nav(key: str) -> dict:
    # serves navigation config to template
    return NAVIGATION[key]


@register.filter
def get_type(value):
    return str(type(value)).replace("<class '", '').replace("'>", '')


@register.filter
def get_value(data: dict, key: (str, int)):
    if hasattr(data, 'get'):
        return data.get(key, None)

    if hasattr(data, key):
        return getattr(data, key)

    return None


@register.filter
def get_fallback(data, fallback):
    return data if data not in [None, ''] else fallback


@register.filter
def exists(data: (dict, list, str, bool)) -> bool:
    if data is None:
        return False

    if isinstance(data, bool):
        return data

    if isinstance(data, (list, dict)):
        return len(data) > 0

    if isinstance(data, str):
        return data.strip() != ''

    return False


@register.filter
def get_choice(choices: list[tuple[int, any]], idx: int):
    return choices[idx][1]


@register.filter
def to_dict(data):
    return data.__dict__


@register.filter
def ignore_none(data):
    if data is None:
        return ''

    return data


@register.filter
def capitalize(data: str) -> str:
    return data.capitalize()


@register.filter
def whitespace_char(data: str, char: str) -> str:
    return data.replace(char, ' ')


@register.filter
def split(data: str, split_at: str) -> list:
    return data.split(split_at)


@register.filter
def find(data: str, search: str) -> bool:
    if not isinstance(data, str):
        data = str(data)

    return data.find(search) != -1
