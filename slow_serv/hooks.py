import base64
import hashlib
import logging
from typing import Callable, Dict, Optional, Union
import config
import json

from slow_serv.secret_cookie import decrypt, encrypt
from slow_serv.req.req import Request
from slow_serv.resp.resp import Response

hooks: Dict[str, Callable] = {}


def secret_cookie_middleware_before(request: Request, response: Response):
    cookie = request.cookie
    ciphered_secret_cookie = cookie.get("secret_cookie")

    if ciphered_secret_cookie:
        byte_secret_cookie = decrypt(
            ciphered_secret_cookie.encode(),
            base64.urlsafe_b64encode(hashlib.sha256(config.SECRET_KEY.encode()).digest()),
        )
        if byte_secret_cookie:
            response.secret_cookie = json.loads(byte_secret_cookie.decode())
        else:
            response.secret_cookie = {}
    else:
        response.secret_cookie = {}


def exit_with_invalid_cookie():
    logging.info("Secret cookie tempered!")
    exit()

from urllib import parse
parse.quote