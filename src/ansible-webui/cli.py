#!/usr/bin/env python3

from sys import exit as sys_exit
from os import geteuid
from os import stat
from os import path
from argparse import ArgumentParser

from aw.config.hardcoded import KEY_TIME_FORMAT

from cli_init import init_cli

# pylint: disable=C0415


def _api_key(action: str, username: str):
    # python3 -m ansible-webui.cli -f api-key -a create -p <username>
    from aw.base import USERS
    from aw.model.api import AwAPIKey
    from aw.utils.util import datetime_w_tz

    if action == 'create':
        user = USERS.objects.get(username=username)
        token = f'{user}-{datetime_w_tz().strftime(KEY_TIME_FORMAT)}'
        _, key = AwAPIKey.objects.create_key(name=token, user=user)
        print(f'API Key created:\nToken={token}\nKey={key}')
        sys_exit(0)

    sys_exit(1)


def main():
    file_owner_uid = stat(path.dirname(path.abspath(__file__))).st_uid
    if geteuid() not in [0, file_owner_uid]:
        print('ERROR: Only root and the code-owner are permitted to run this script!')
        sys_exit(1)

    init_cli()

    parser = ArgumentParser()
    parser.add_argument(
        '-f', '--function', type=str, required=True,
        choices=['api-key'],
    )
    parser.add_argument(
        '-a', '--action', type=str, required=True,
        choices=['create'],
    )
    parser.add_argument('-p', '--parameter', type=str, required=True)
    args = parser.parse_args()

    if args.function == 'api-key':
        _api_key(action=args.action, username=args.parameter)


if __name__ == '__main__':
    main()
