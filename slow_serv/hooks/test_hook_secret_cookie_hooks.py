import hashlib
import base64
import json
from slow_serv.resp.cookie import CookieItem

from slow_serv.req.req import Request
from slow_serv.resp.resp import Response
from slow_serv.hooks.hook_secret_cookie import (
    cipher,
    decipher,
    secret_cookie_before,
    secret_cookie_after,
)
import config


def test_cipher_decipher():
    data = b"123"
    key = base64.b64encode(hashlib.sha256(b"abcde").digest())

    ciphered_byte = cipher(data, key)
    new_data = decipher(ciphered_byte, key)
    assert data == new_data

    # If the ciphered_byte has been tampered, new_data should equals to b""
    new_data = decipher(b"123", key)
    assert b"" == new_data


def test_secret_cookie_before_1():
    """
    When the request contains no secret_cookie
    """
    req = Request("GET", {})
    resp = Response()
    req.cookie = {"k1": "1", "k2": "2"}
    secret_cookie_before(req, resp)
    assert resp.secret_cookie == {}


def test_secret_cookie_before_2():
    """
    When the request contains secret_cookie,
    we test by seeing if the original secret_cookie_dict == resp.secret_cookie
    """
    req = Request("GET", {})
    resp = Response()
    sc_dict = {"a": "1", "b": "2"}
    key = base64.b64encode(hashlib.sha256(config.SECRET_KEY.encode()).digest())
    ciphered_byte = cipher(json.dumps(sc_dict).encode(), key)
    req.cookie = {"k1": "1", "k2": "2"}
    req.cookie["secret_cookie"] = ciphered_byte.decode()
    secret_cookie_before(req, resp)
    assert resp.secret_cookie == sc_dict


def test_secret_cookie_after_1():
    """
    When there is nothing in resp.secret_cookie, then after executing
    after-hook, there should be no key="secret_cookie" in resp.cookie
    """
    req = Request("GET", {})
    resp = Response()
    secret_cookie_after(req, resp)
    assert "secret_cookie" not in resp.cookie


def test_secret_cookie_after_2():
    """
    When there is something in resp.secret_cookie, 
    we test by seeing if resp.cookie["secret_cookie"] == our_manually_ciphered_cookie_str
    """
    req = Request("GET", {})
    resp = Response()
    resp.secret_cookie = {"a": "1", "b": "2"}
    secret_cookie_after(req, resp)

    # Generate our_manually_ciphered_cookie_str
    key = base64.b64encode(hashlib.sha256(config.SECRET_KEY.encode()).digest())
    ciphered_byte = cipher(json.dumps(resp.secret_cookie).encode(), key)
    res = ciphered_byte.decode()

    assert "secret_cookie" in resp.cookie
    assert isinstance(resp.cookie["secret_cookie"], CookieItem)

    # NOTE: Since AES-CBC generate iv randomly, we should not test if the
    # ciphered_str are the same.
    # So we need to decipher the ciphered_str, and test them if are the same
    # assert resp.cookie["secret_cookie"] == res # WRONG!

    # print(decipher(resp.cookie["secret_cookie"].encode(), key))
    # print(decipher(res.encode(), key))
    assert decipher(resp.cookie["secret_cookie"].val.encode(), key) == decipher(
        res.encode(), key
    )

