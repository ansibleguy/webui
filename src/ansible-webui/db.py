from pathlib import Path
from shutil import copy
from datetime import datetime
from sys import exit as sys_exit
from secrets import choice as random_choice
from string import digits, ascii_letters
from os import listdir, remove
from time import time

from aw.settings import DB_FILE
from aw.utils.subps import process
from aw.utils.debug import log, log_error, log_warn
from aw.utils.deployment import deployment_prod
from aw.config.hardcoded import FILE_TIME_FORMAT
from aw.config.environment import check_aw_env_var_true, get_aw_env_var, check_aw_env_var_is_set

DB_BACKUP_EXT = '.auto.bak'
DB_BACKUP_RETENTION_DAYS = 7

if not deployment_prod():
    DB_BACKUP_RETENTION_DAYS = 1

DB_BACKUP_RETENTION = DB_BACKUP_RETENTION_DAYS * 24 * 60 * 60


def install_or_migrate_db():
    if not Path(DB_FILE).is_file():
        return install()

    return migrate()


def _manage_db(action: str, cmd: list, backup: str = None) -> str:
    cmd2 = ['python3', 'manage.py']
    cmd2.extend(cmd)

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

    return result['stdout']


def _clean_old_db_backups():
    possible_db_backup_files = listdir(DB_FILE.parent)
    for file in possible_db_backup_files:
        if file.startswith(DB_FILE.name) and file.endswith(DB_BACKUP_EXT):
            backup_file = DB_FILE.parent / file
            backup_age = time() - backup_file.stat().st_mtime
            if backup_age > DB_BACKUP_RETENTION:
                log(msg=f"Cleaning old backup file: '{backup_file}'", level=4)
                remove(backup_file)


def install():
    log(msg=f"Initializing database {DB_FILE}..", level=3)
    _make_migrations()
    _manage_db(action='initialization', cmd=['migrate'])


def migrate():
    _clean_old_db_backups()
    migration_needed = _make_migrations()

    if migration_needed and check_aw_env_var_true('db_migrate'):
        backup = f"{DB_FILE}.{datetime.now().strftime(FILE_TIME_FORMAT)}{DB_BACKUP_EXT}"
        log(msg=f"Creating database backup: '{backup}'", level=6)
        copy(src=DB_FILE, dst=backup)

        log(msg=f"Upgrading database {DB_FILE}", level=3)
        _manage_db(action='migration', cmd=['migrate'], backup=backup)


def _make_migrations() -> bool:
    changed = False

    for stdout in [
        _manage_db(action='schema-creation', cmd=['makemigrations']),
        _manage_db(action='schema-creation', cmd=['makemigrations', 'aw']),
    ]:
        if stdout.find('No changes detected') == -1:
            changed = True

    return changed


def create_first_superuser():
    # pylint: disable=C0415
    from aw.base import USERS
    if len(USERS.objects.filter(is_superuser=True)) == 0:
        name = get_aw_env_var('init_admin')
        pwd = get_aw_env_var('init_admin_pwd')

        if name is None:
            name = 'ansible'

        if pwd is None:
            pwd = ''.join(random_choice(ascii_letters + digits + '!.-+') for _ in range(14))

        USERS.objects.create_superuser(
            username=name,
            email=f"{name}@localhost",
            password=pwd
        )

        log_warn('No admin was found in the database!')
        if check_aw_env_var_is_set('init_admin_pwd'):
            log(msg=f"The user '{name}' was created!", level=4)

        else:
            log(msg=f"Generated user: '{name}'", level=3)
            log(msg=f"Generated pwd: '{pwd}'", level=3)
            log_warn('Make sure to change the password!')
