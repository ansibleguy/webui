from base64 import b64encode, b64decode
from hashlib import sha256

from Crypto import Random
from Crypto.Cipher import AES

from aw.config.main import config
from aw.utils.util import is_null
from aw.utils.debug import log_warn

__KEY = sha256(config['secret'].encode()).digest()


def encrypt(raw: str) -> str:
    if is_null(raw):
        return ''

    raw = _pad(raw)
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(__KEY, AES.MODE_CBC, iv)
    return b64encode(iv + cipher.encrypt(raw.encode())).decode('utf-8')


def decrypt(enc: str) -> str:
    if is_null(enc):
        return ''

    try:
        enc = b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(__KEY, AES.MODE_CBC, iv)
        return _unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    except ValueError:
        log_warn("Unable to decrypt secret! Maybe the key 'AW_SECRET' changed?")
        return ''


def _pad(s) -> str:
    bs = AES.block_size
    return s + (bs - len(s) % bs) * chr(bs - len(s) % bs)


def _unpad(s) -> bytes:
    return s[:-ord(s[len(s)-1:])]
