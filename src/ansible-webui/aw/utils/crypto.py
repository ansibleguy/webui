from base64 import b64encode, b64decode
from hashlib import sha256

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

from aw.config.main import config
from aw.utils.util import is_null
from aw.utils.debug import log_warn, log

__KEY = sha256(config['secret'].encode('utf-8')).digest()


def encrypt(plaintext: str) -> str:
    if is_null(plaintext):
        return ''

    try:
        return _encrypt(plaintext.encode('utf-8')).decode('utf-8')

    except ValueError as err:
        log_warn("Unable to encrypt data!")
        log(msg=f"Got error encrypting plaintext: '{err}'", level=6)
        return ''


def _encrypt(plaintext: bytes) -> bytes:
    iv = get_random_bytes(AES.block_size)
    cipher = AES.new(__KEY, AES.MODE_CBC, iv)
    ciphertext = iv + cipher.encrypt(
        plaintext=pad(
            data_to_pad=plaintext,
            block_size=AES.block_size,
            style='pkcs7',
        ),
    )
    return b64encode(ciphertext)


def decrypt(ciphertext: str) -> str:
    if is_null(ciphertext):
        return ''

    try:
        return _decrypt(ciphertext.encode('utf-8')).decode('utf-8')

    except ValueError as err:
        log_warn("Unable to decrypt secret! Maybe the key 'AW_SECRET' changed?")
        log(msg=f"Got error decrypting ciphertext: '{err}'", level=6)
        return ''


def _decrypt(ciphertext: bytes) -> bytes:
    ciphertext = b64decode(ciphertext)
    cipher = AES.new(__KEY, AES.MODE_CBC, ciphertext[:AES.block_size])
    return unpad(
        padded_data=cipher.decrypt(ciphertext[AES.block_size:]),
        block_size=AES.block_size,
        style='pkcs7',
    )
