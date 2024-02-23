# pylint: disable=W0401,W0614,E0102
from django.db.backends.sqlite3.base import *


# NOTE: quick-patch for https://github.com/django/django/commit/a0204ac183ad6bca71707676d994d5888cf966aa
#   todo: remove once feature is available natively in django 5.1

class DatabaseWrapper(DatabaseWrapper):
    def _start_transaction_under_autocommit(self):
        self.cursor().execute('BEGIN IMMEDIATE')
