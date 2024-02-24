#!/usr/bin/env python3

from sys import argv as sys_argv

from cli import init_cli

# pylint: disable=C0415


def main():
    init_cli()
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys_argv)


if __name__ == '__main__':
    main()
