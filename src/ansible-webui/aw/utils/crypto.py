from base64 import b64encode, b64decode
from hashlib import sha256

from Crypto import Random
from Crypto.Cipher import AES

from aw.config.main import config

__KEY = sha256(config['secret'].encode()).digest()


def encrypt(raw):
    raw = _pad(raw)
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(__KEY, AES.MODE_CBC, iv)
    return b64encode(iv + cipher.encrypt(raw.encode())).decode('utf-8')


def decrypt(enc):
    enc = b64decode(enc)
    iv = enc[:AES.block_size]
    cipher = AES.new(__KEY, AES.MODE_CBC, iv)
    return _unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')


def _pad(s):
    bs = AES.block_size
    return s + (bs - len(s) % bs) * chr(bs - len(s) % bs)


def _unpad(s):
    return s[:-ord(s[len(s)-1:])]
