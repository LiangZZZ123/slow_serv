from secret_cookie import do_encrypt, de_encrypt


def test_cookie_encrypt():
    data = "123"
    key = "secret"

    ciphertext, nonce = do_encrypt(data, key)
    new_data = de_encrypt(ciphertext, key, nonce)
    assert data == new_data
