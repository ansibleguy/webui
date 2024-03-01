#!/usr/bin/env python3

from sys import exit as sys_exit
from sys import argv as sys_argv
from sys import path as sys_path
from os import path as os_path
from os import geteuid, stat, listdir
from argparse import ArgumentParser
from json import dumps as json_dumps
from pathlib import Path

# pylint: disable=C0415


def _api_key(username: str):
    # python3 -m ansibleguy-webui.cli api-key.create
    from aw.base import USERS
    from aw.model.api import AwAPIKey
    from aw.utils.util import datetime_w_tz
    from aw.config.hardcoded import KEY_TIME_FORMAT

    user = USERS.objects.get(username=username)
    token = f'{user}-{datetime_w_tz().strftime(KEY_TIME_FORMAT)}'
    _, key = AwAPIKey.objects.create_key(name=token, user=user)
    print(f'API Key created:\nToken={token}\nKey={key}')
    sys_exit(0)


def _print_version():
    # python3 -m ansibleguy-webui.cli --version
    from aw.utils.version import get_version, get_system_versions

    print(f'Version: {get_version()}\n{json_dumps(get_system_versions(), indent=4)}')
    sys_exit(0)


def _list_migrations(module_base: str):
    print('Migrations')
    migrations = listdir(Path(module_base) / 'aw' / 'migrations')
    migrations.sort()
    for mig in migrations:
        if mig.find('_v') != -1:
            version = mig.split('_', 1)[1][1:-3].replace('_', '.')
            print(f"  Version: {version}: {mig}")

    sys_exit(0)


def main():
    this_file = os_path.abspath(__file__)
    file_owner_uid = stat(this_file).st_uid
    if geteuid() not in [0, file_owner_uid]:
        print('ERROR: Only root and the code-owner are permitted to run this script!')
        sys_exit(1)

    module_base = os_path.dirname(this_file)
    # pylint: disable=E0401,C0415
    try:
        from cli_init import init_cli

    except ModuleNotFoundError:
        sys_path.append(module_base)
        from cli_init import init_cli

    init_cli()

    if len(sys_argv) > 1:
        if sys_argv[1] in ['-v', '--version']:
            _print_version()

    parser = ArgumentParser()
    parser.add_argument(
        '-a', '--action', type=str, required=True,
        choices=['api-key.create', 'migrations.list'],
    )
    parser.add_argument('-p', '--parameter', type=str, required=False)
    args = parser.parse_args()

    if args.action == 'api-key.create' and args.parameter is not None:
        _api_key(username=args.parameter)

    if args.action == 'migrations.list':
        _list_migrations(module_base)


if __name__ == '__main__':
    main()
