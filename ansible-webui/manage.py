#!/usr/bin/env python3

from os import environ
from sys import argv as sys_argv


def main():
    environ.setdefault('DJANGO_SETTINGS_MODULE', 'aw.settings')

    # pylint: disable=E0401,C0415
    from aw.config.main import init_globals
    init_globals()

    try:
        # pylint: disable=C0415
        from django.core.management import execute_from_command_line

    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    execute_from_command_line(sys_argv)


if __name__ == '__main__':
    main()
