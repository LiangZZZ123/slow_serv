from typing import Tuple
import config
import hashlib
from Crypto.Cipher import AES
from cryptography.fernet import Fernet


# def encrypt(data: str, key: str) -> Tuple[bytes, bytes]:
#     key_digest = hashlib.md5(key.encode()).digest()
#     cipher = AES.new(key_digest, mode=AES.MODE_GCM)
#     # cipher = AES.new(key, mode = AES.MODE_EAX)

#     """
#     to ensure that encrypting the same plaintext many times with the same key
#     does not produce the same ciphertext (which risks the possibility that an
#     eavesdropper might learn something from frequency analysis, the so called
#     "replay attack").
#     """
#     nonce = cipher.nonce  # type:ignore
#     ciphertext, tag = cipher.encrypt_and_digest(data.encode())  # type:ignore
#     return ciphertext, nonce


# def decrypt(ciphertext: bytes, key: str, nonce: bytes) -> str:
#     key_digest = hashlib.md5(key.encode()).digest()
#     try:
#         cipher = AES.new(key_digest, mode=AES.MODE_GCM, nonce=nonce)
#         deciphered_binary = cipher.decrypt(ciphertext)
#         data = deciphered_binary.decode()
#     except UnicodeDecodeError:
#         data = ""

#     return data


# def encrypt(data: bytes, key: bytes) -> bytes:
#     cipher = AES.new(key, mode=AES.MODE_CFB)
#     # length = 16 - (len(data) % 16)
#     # data += bytes([length]) * length
#     encrypted_data = cipher.encrypt(data)
#     return encrypted_data


# def decrypt(encrypted_data: bytes, key: bytes) -> bytes:
#     # try:
#     cipher = AES.new(key, mode=AES.MODE_CFB)
#     data = cipher.decrypt(encrypted_data)
#     # except UnicodeDecodeError:
#     #     str_data = ""
#     # print(data)
#     # data = data[: -data[-1]]

#     return data


def encrypt(data: bytes, key: bytes) -> bytes:
    cipher = Fernet(key)
    binary_ciphertext = cipher.encrypt(data)
    return binary_ciphertext


def decrypt(str_ciphertext: bytes, key: bytes) -> bytes:
    cipher = Fernet(key)
    try:
        data = cipher.decrypt(str_ciphertext)
    except UnicodeDecodeError:
        data = b""

    return data

