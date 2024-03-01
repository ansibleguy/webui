from django.apps import AppConfig
from django.dispatch import receiver
from django.db.backends.signals import connection_created


class AwConfig(AppConfig):
    name = 'aw'
    verbose_name = 'Ansible-WebUI'


# configuring sqlite at application startup/connection initialization
@receiver(connection_created)
def configure_sqlite(connection, **kwargs):
    if connection.vendor == 'sqlite':
        with connection.cursor() as cursor:
            # https://www.sqlite.org/pragma.html#pragma_journal_mode
            cursor.execute('PRAGMA journal_mode = WAL;')
            # https://www.sqlite.org/pragma.html#pragma_busy_timeout
            cursor.execute('PRAGMA busy_timeout = 5000;')
            # https://www.sqlite.org/pragma.html#pragma_synchronous
            cursor.execute('PRAGMA synchronous = NORMAL;')
