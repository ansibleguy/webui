from os import environ
from os import path as os_path
from sys import path as sys_path

from django import setup as django_setup


def init_cli():
    # workaround for CI
    if 'AW_VERSION' not in environ:
        environ['AW_VERSION'] = '0.0.0'

    # pylint: disable=E0401,C0415
    try:
        from aw.config.main import init_globals

    except ModuleNotFoundError:
        sys_path.append(os_path.dirname(os_path.abspath(__file__)))
        from aw.config.main import init_globals

    init_globals()
    from aw.utils.debug import warn_if_development
    warn_if_development()

    django_setup()
