from pathlib import Path
from shutil import copy
from datetime import datetime
from sys import exit as sys_exit
from os import environ
from secrets import choice as random_choice
from string import digits, ascii_letters

from aw.settings import DB_FILE
from aw.utils.subps import process
from aw.utils.debug import log, log_error, log_warn


ENV_KEY_INIT_ADMIN_NAME = 'AW_ADMIN'
ENV_KEY_INIT_ADMIN_PWD = 'AW_ADMIN_PWD'


def install_or_migrate_db():
    if not Path(DB_FILE).is_file():
        return install()

    return migrate()


def _manage_db(action: str, cmd: list, backup: str = None):
    cmd2 = ['python3', 'manage.py']
    cmd2.extend(cmd)

    log(msg=f"Executing DB-management command: '{cmd2}'", level=6)
    result = process(cmd=cmd2)

    if result['rc'] != 0:
        log_error(f'Database {action} failed!')
        log(msg=f"Error:\n{result['stderr']}", level=1)
        log(msg=f"Output:\n{result['stdout']}", level=3)

        if backup is not None:
            log_warn(
                msg=f"Trying to restore database from automatic backup: {backup} => {DB_FILE}",
                _stderr=True,
            )
            copy(src=DB_FILE, dst=f'{backup}.failed')
            copy(src=backup, dst=DB_FILE)

        else:
            sys_exit(1)


def install():
    log(msg=f"Initializing database {DB_FILE}..", level=3)
    _make_migrations()
    _manage_db(action='initialization', cmd=['migrate'])


def migrate():
    _make_migrations()

    backup = f"{DB_FILE}.{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.bak"
    log(msg=f"Creating database backup: '{backup}'", level=6)
    copy(src=DB_FILE, dst=backup)

    if 'AW_DB_MIGRATE' not in environ:
        log(msg=f"Migrating database {DB_FILE}..", level=3)
        _manage_db(action='migration', cmd=['migrate'], backup=backup)


def _make_migrations():
    _manage_db(action='schema-creation', cmd=['makemigrations'])
    _manage_db(action='schema-creation', cmd=['makemigrations', 'aw'])


def create_first_superuser():
    # pylint: disable=C0415
    from django.contrib.auth.models import User
    if len(User.objects.filter(is_superuser=True)) == 0:
        name = 'ansible'
        pwd = ''.join(random_choice(ascii_letters + digits + '!.-+') for _ in range(14))

        if ENV_KEY_INIT_ADMIN_NAME in environ:
            name = environ[ENV_KEY_INIT_ADMIN_NAME]

        if ENV_KEY_INIT_ADMIN_PWD in environ:
            pwd = environ[ENV_KEY_INIT_ADMIN_PWD]

        User.objects.create_superuser(
            username=name,
            email=f"{name}@localhost",
            password=pwd
        )

        log_warn('No admin was found in the database!')
        if ENV_KEY_INIT_ADMIN_PWD in environ:
            log(msg='The user was created as provided!', level=4)

        else:
            log(msg=f"Generated user: '{name}'", level=3)
            log(msg=f"Generated pwd: '{pwd}'", level=3)
            log_warn('Make sure to change the password!')
