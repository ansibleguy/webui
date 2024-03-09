from functools import cache

from django import template

from aw.config.main import config
from aw.settings import STATIC_URL, AUTH_MODE
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
def auth_sso(_) -> bool:
    return AUTH_MODE == 'saml'


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


# see: https://github.com/grafana/django-saml2-auth/blob/main/django_saml2_auth/errors.py
SAML_ERROR_CODES = {
    1100: 'EMPTY_FUNCTION_PATH',
    1101: 'PATH_ERROR',
    1102: 'IMPORT_ERROR',
    1103: 'GENERAL_EXCEPTION',
    1104: 'CREATE_USER_ERROR',
    1105: 'GROUP_JOIN_ERROR',
    1106: 'NO_REVERSE_MATCH',
    1107: 'ERROR_CREATING_SAML_CONFIG_OR_CLIENT',
    1108: 'NO_SAML_RESPONSE_FROM_CLIENT',
    1109: 'NO_SAML_RESPONSE_FROM_IDP',
    1110: 'NO_NAME_ID_IN_SAML_RESPONSE',
    1111: 'NO_ISSUER_IN_SAML_RESPONSE',
    1112: 'NO_USER_IDENTITY_IN_SAML_RESPONSE',
    1113: 'NO_TOKEN_SPECIFIED',
    1114: 'NO_USERNAME_OR_EMAIL_SPECIFIED',
    1115: 'SHOULD_NOT_CREATE_USER',
    1116: 'INACTIVE_USER',
    1117: 'NO_METADATA_URL_OR_FILE',
    1118: 'NO_SAML_CLIENT',
    1119: 'NO_JWT_ALGORITHM',
    1120: 'INVALID_METADATA_URL',
    1121: 'NO_METADATA_URL_ASSOCIATED',
    1122: 'INVALID_REQUEST_METHOD',
    1123: 'CANNOT_DECODE_JWT_TOKEN',
    1124: 'USER_MISMATCH',
    1125: 'NO_JWT_SECRET',
    1126: 'NO_JWT_PRIVATE_KEY',
    1127: 'NO_JWT_PUBLIC_KEY',
    1128: 'INVALID_JWT_ALGORITHM',
    1129: 'NO_USER_ID',
    1130: 'INVALID_TOKEN',
    1131: 'INVALID_NEXT_URL',
}


@register.filter
def saml_error_by_code(error_code: int) -> str:
    if error_code not in SAML_ERROR_CODES:
        return ''

    return f" ({SAML_ERROR_CODES[error_code]})"
