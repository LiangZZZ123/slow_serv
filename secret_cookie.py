from typing import Tuple
import config
import hashlib
from Crypto.Cipher import AES


def do_encrypt(data: str, key: str) -> Tuple[bytes, bytes]:
    key_digest = hashlib.md5(key.encode()).digest()
    cipher = AES.new(key_digest, mode=AES.MODE_GCM)
    # cipher = AES.new(key, mode = AES.MODE_EAX)

    """
    to ensure that encrypting the same plaintext many times with the same key 
    does not produce the same ciphertext (which risks the possibility that an 
    eavesdropper might learn something from frequency analysis, the so called 
    "replay attack").
    """
    nonce = cipher.nonce  # type:ignore
    ciphertext, tag = cipher.encrypt_and_digest(data.encode())  # type:ignore
    return ciphertext, nonce


def de_encrypt(ciphertext: bytes, key: str, nonce: bytes) -> str:
    key_digest = hashlib.md5(key.encode()).digest()
    try:
        cipher = AES.new(key_digest, mode=AES.MODE_GCM, nonce=nonce)
        deciphered_binary = cipher.decrypt(ciphertext)
        data = deciphered_binary.decode()
    except UnicodeDecodeError:
        data = ""

    return data
