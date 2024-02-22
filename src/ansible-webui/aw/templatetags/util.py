from pathlib import Path
from datetime import datetime
from functools import cache

from django import template

from aw.config.main import VERSION
from aw.config.navigation import NAVIGATION
from aw.utils.subps import process
from aw.config.hardcoded import LOG_TIME_FORMAT

register = template.Library()


@cache
@register.simple_tag
def get_version() -> str:
    if VERSION == 'latest' or VERSION.find('dev') != -1 or VERSION.find('staging') != -1:
        this_file = Path(__file__)
        repo_base = this_file.resolve().parent.parent.parent.parent.parent
        if (repo_base / '.git').is_dir():
            commit = process(cmd=['git', 'rev-parse', '--short', 'HEAD'], cwd=repo_base)['stdout'].strip()
            if commit != '':
                return f'{VERSION} ({commit})'

        else:
            mod_time = this_file.stat().st_mtime
            mod_time = datetime.fromtimestamp(mod_time).strftime(LOG_TIME_FORMAT)
            return f'{VERSION} ({mod_time})'

    return VERSION


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
