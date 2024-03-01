from pathlib import Path
from shutil import copy
from datetime import datetime
from sys import exit as sys_exit
from secrets import choice as random_choice
from string import digits, ascii_letters
from os import listdir, remove
from time import time
from sqlite3 import connect as db_connect
from sqlite3 import OperationalError

from aw.config.main import VERSION
from aw.settings import DB_FILE
from aw.utils.subps import process
from aw.utils.debug import log, log_error, log_warn
from aw.utils.deployment import deployment_prod, is_release_version
from aw.config.hardcoded import FILE_TIME_FORMAT, GRP_MANAGER
from aw.config.environment import check_aw_env_var_true, get_aw_env_var, check_aw_env_var_is_set

DB_BACKUP_EXT = '.auto.bak'
DB_BACKUP_RETENTION_DAYS = 7

if not deployment_prod():
    DB_BACKUP_RETENTION_DAYS = 1

DB_BACKUP_RETENTION = DB_BACKUP_RETENTION_DAYS * 24 * 60 * 60


def _check_if_writable():
    try:
        test_file = DB_FILE.parent / '.awtest'
        with open(test_file, 'w', encoding='utf-8') as _file:
            _file.write('TEST')

        remove(test_file)

    except PermissionError:
        log(msg=f"Error: DB directory is not writable: '{DB_FILE.parent}'")
        sys_exit(1)


def _schema_up_to_date() -> bool:
    if not Path(DB_FILE).is_file():
        return False

    try:
        with db_connect(DB_FILE) as conn:
            return conn.execute('SELECT schema_version FROM aw_schemametadata').fetchall()[0][0] == VERSION

    except (IndexError, OperationalError):
        return False


def _get_current_schema_version() -> (str, None):
    try:
        with db_connect(DB_FILE) as conn:
            return conn.execute('SELECT schema_version FROM aw_schemametadata').fetchall()[0][0]

    except (IndexError, OperationalError):
        return None


def _update_schema_version() -> None:
    previous = _get_current_schema_version()

    with db_connect(DB_FILE) as conn:
        try:
            if previous is None:
                conn.execute(
                    "INSERT INTO aw_schemametadata (created, updated, schema_version) VALUES "
                    f"(DATETIME('now'), DATETIME('now'), '{VERSION}')",
                )

            else:
                conn.execute(
                    "UPDATE aw_schemametadata SET "
                    f"schema_version = '{VERSION}', schema_version_prev = '{previous}', "
                    "updated = DATETIME('now') WHERE id = 1"
                )

            conn.commit()

        except (IndexError, OperationalError) as err:
            log(msg=f"Error updating database schema version: '{err}'", level=3)


def install_or_migrate_db():
    log(msg=f"Using DB: {DB_FILE}", level=4)
    _check_if_writable()
    if not Path(DB_FILE).is_file():
        return install()

    return migrate()


def _manage_db(action: str, cmd: list, backup: str = None) -> dict:
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

    return result


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
    _migration_needed()
    _manage_db(action='initialization', cmd=['migrate'])
    _update_schema_version()


def migrate():
    _clean_old_db_backups()

    if _migration_needed() and check_aw_env_var_true(var='db_migrate', fallback=True):
        backup = f"{DB_FILE}.{datetime.now().strftime(FILE_TIME_FORMAT)}{DB_BACKUP_EXT}"
        log(msg=f"Creating database backup: '{backup}'", level=6)
        copy(src=DB_FILE, dst=backup)

        log(msg=f"Upgrading database {DB_FILE}", level=3)
        if _manage_db(action='migration', cmd=['migrate'], backup=backup)['rc'] == 0:
            _update_schema_version()


def _migration_needed() -> bool:
    if is_release_version():
        # stable versions should only have released migrations
        return not _schema_up_to_date()

    changed = False

    for stdout in [
        _manage_db(action='schema-creation', cmd=['makemigrations'])['stdout'],
        _manage_db(action='schema-creation', cmd=['makemigrations', 'aw'])['stdout'],
    ]:
        if stdout.find('No changes detected') == -1:
            changed = True

    return changed or not _schema_up_to_date()


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


def create_privileged_groups():
    # pylint: disable=C0415
    from django.contrib.auth.models import Group
    for grp in GRP_MANAGER.values():
        Group.objects.get_or_create(name=grp)
