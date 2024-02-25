from django.db import models

from aw.model.base import BaseModel, DEFAULT_NONE
from aw.utils.util import is_null, is_set
from aw.utils.crypto import decrypt, encrypt
from aw.base import USERS


class BaseJobCredentials(BaseModel):
    SECRET_ATTRS = ['become_pass', 'vault_pass', 'connect_pass', 'ssh_key']
    SECRET_ATTRS_ARGS = {
        'vault_pass': 'vault-password-file',
        'become_pass': 'become-password-file',
        'connect_pass': 'connection-password-file',
        'ssh_key': 'key-file',
    }
    PUBLIC_ATTRS_ARGS = {
        'connect_user': '--user',
        'become_user': '--become-user',
        'vault_file': '--vault-password-file',
        'vault_id': '--vault-id',
    }
    SECRET_HIDDEN = '⬤' * 15

    name = models.CharField(max_length=100, null=False, blank=False)
    connect_user = models.CharField(max_length=100, **DEFAULT_NONE)
    become_user = models.CharField(max_length=100, default='root', null=True, blank=True)
    # default become_user according to ansible-playbook docs
    vault_file = models.CharField(max_length=300, **DEFAULT_NONE)
    vault_id = models.CharField(max_length=50, **DEFAULT_NONE)

    _enc_vault_pass = models.CharField(max_length=500, **DEFAULT_NONE)
    _enc_become_pass = models.CharField(max_length=500, **DEFAULT_NONE)
    _enc_connect_pass = models.CharField(max_length=500, **DEFAULT_NONE)
    _enc_ssh_key = models.CharField(max_length=5000, **DEFAULT_NONE)

    @property
    def vault_pass(self) -> str:
        if is_null(self._enc_vault_pass):
            return ''

        return decrypt(self._enc_vault_pass)

    @vault_pass.setter
    def vault_pass(self, value: str):
        if is_null(value):
            self._enc_vault_pass = None
            return

        self._enc_vault_pass = encrypt(value)

    @property
    def vault_pass_is_set(self) -> bool:
        return is_set(self._enc_vault_pass)

    @property
    def become_pass(self) -> str:
        if is_null(self._enc_become_pass):
            return ''

        return decrypt(self._enc_become_pass)

    @become_pass.setter
    def become_pass(self, value: str):
        if is_null(value):
            self._enc_become_pass = None
            return

        self._enc_become_pass = encrypt(value)

    @property
    def become_pass_is_set(self) -> bool:
        return is_set(self._enc_become_pass)

    @property
    def connect_pass(self) -> str:
        if is_null(self._enc_connect_pass):
            return ''

        return decrypt(self._enc_connect_pass)

    @connect_pass.setter
    def connect_pass(self, value: str):
        if is_null(value):
            self._enc_connect_pass = None
            return

        self._enc_connect_pass = encrypt(value)

    @property
    def connect_pass_is_set(self) -> bool:
        return is_set(self._enc_connect_pass)

    @property
    def ssh_key(self) -> str:
        if is_null(self._enc_ssh_key):
            return ''

        return decrypt(self._enc_ssh_key)

    @ssh_key.setter
    def ssh_key(self, value: str):
        if is_null(value):
            self._enc_ssh_key = None
            return

        self._enc_ssh_key = encrypt(value)

    @property
    def ssh_key_is_set(self) -> bool:
        return is_set(self._enc_ssh_key)

    def _get_set_creds_str(self) -> str:
        creds_set = [attr for attr in self.SECRET_ATTRS if is_set(getattr(self, attr))]
        creds_set_str = ''
        if len(creds_set) > 0:
            creds_set_str = f" ({', '.join(creds_set)})"

        return creds_set_str

    class Meta:
        abstract = True


class JobGlobalCredentials(BaseJobCredentials):
    api_fields_read = [
        'id', 'name', 'become_user', 'connect_user', 'vault_file', 'vault_id'
    ]
    api_fields_write = api_fields_read.copy()
    api_fields_write.extend(BaseJobCredentials.SECRET_ATTRS)
    for secret_attr in BaseJobCredentials.SECRET_ATTRS:
        api_fields_read.append(f'{secret_attr}_is_set')
    form_fields = api_fields_write

    def __str__(self) -> str:
        return f"Global credentials '{self.name}'{self._get_set_creds_str()}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name'], name='jobcreds_name')
        ]


class JobUserCredentials(BaseJobCredentials):
    api_fields_read = JobGlobalCredentials.api_fields_read.copy()
    api_fields_read.append('user')
    api_fields_write = JobGlobalCredentials.api_fields_write.copy()
    api_fields_write.append('user')
    form_fields = JobGlobalCredentials.api_fields_write.copy()

    user = models.ForeignKey(USERS, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"Credentials '{self.name}' of user '{self.user.username}'{self._get_set_creds_str()}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'name'], name='jobusercreds_user_name')
        ]
