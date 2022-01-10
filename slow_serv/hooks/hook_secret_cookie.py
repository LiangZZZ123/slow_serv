import base64
import hashlib
import logging
import json
from Crypto.Cipher import AES
import cryptography
from cryptography.fernet import Fernet
from typing import Callable, Dict, Optional, Union

import config
from slow_serv.req.req import Request
from slow_serv.resp.resp import Response

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


def cipher(plain_byte: bytes, key: bytes) -> bytes:
    cipher = Fernet(key)
    cipherted_byte = cipher.encrypt(plain_byte)
    return cipherted_byte


def decipher(ciphered_byte: bytes, key: bytes) -> bytes:
    cipher = Fernet(key)
    try:
        # ciphered_byte = b"12345"
        plain_byte = cipher.decrypt(ciphered_byte)
    # If decrypt fails, which means ciphered_byte must have been tampered.
    except cryptography.fernet.InvalidToken:
        plain_byte = b""

    # ciphered_byte = b'12345'
    # plain_byte = cipher.decrypt(ciphered_byte)
    return plain_byte


def secret_cookie_before(request: Request, response: Response):
    """
    1. Check if there's a key="secret_cookie" in request.cookie
    2. If yes, get the corresponding val, which is a ciphered_str, decipher it,
    restore it to "sc_dict", and makes response.secret_cookie = sc_dict
    3. So. if "request.cookie.get('secret_cookie') is not None", then
    "response.secret_cookie = sc_dict"
    4. Here, we use "response.secret_cookie" as a container to hold the sc_dict
    """

    if "secret_cookie" in request.cookie:
        ciphered_str = request.cookie["secret_cookie"]
        plain_byte = decipher(
            ciphered_str.encode(),
            base64.b64encode(hashlib.sha256(config.SECRET_KEY.encode()).digest()),
        )
        if plain_byte != b"":
            sc_dict = json.loads(plain_byte.decode())
            response.secret_cookie = sc_dict
        else:
            logging.info("secret_cookie is been modified!")
            # If secret_cookie has been modified, reset it to an empty dict
            response.secret_cookie = {}


def secret_cookie_after(request: Request, response: Response):
    """
    If we have something as secret cookie, then transfer it from a dict to a 
    ciphered_str, and assign it to response.cookie["secret_cookie"]
    """
    if len(response.secret_cookie) > 0:
        plain_str = json.dumps(response.secret_cookie)
        ciphered_byte = cipher(
            plain_str.encode(),
            base64.b64encode(hashlib.sha256(config.SECRET_KEY.encode()).digest()),
        )

        ciphered_str = ciphered_byte.decode()
        response.cookie["secret_cookie"] = ciphered_str


def exit_with_invalid_cookie():
    logging.info("Secret cookie tempered!")
    exit()

