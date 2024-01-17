#!/usr/bin/env python3

from os import environ
from sys import argv as sys_argv


def main():
    # workaround for CI
    if 'AW_VERSION' not in environ:
        environ['AW_VERSION'] = '0.0.0'

    # pylint: disable=E0401,C0415
    from aw.config.main import init_globals
    init_globals()
    from aw.utils.deployment import warn_if_development
    warn_if_development()

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys_argv)


if __name__ == '__main__':
    main()
