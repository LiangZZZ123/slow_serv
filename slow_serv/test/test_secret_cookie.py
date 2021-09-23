from slow_serv.secret_cookie import encrypt, decrypt
import hashlib
import base64
import os


def test_encrypt_decrypt():
    data = b"123"
    key = base64.urlsafe_b64encode(hashlib.sha256(b"abcde").digest())

    encrypted_data = encrypt(data, key)
    new_data = decrypt(encrypted_data, key)
    assert data == new_data
