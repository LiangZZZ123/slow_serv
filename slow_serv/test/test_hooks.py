from slow_serv.secret_cookie import decrypt, encrypt
from slow_serv.hooks import secret_cookie_middleware_before
import json
import config
from slow_serv.req.req import Request
from slow_serv.resp.resp import Response

def test_secret_cookie_middleware_before():
    # request = Request()
    # response = Response()

    # request.cookie = {""}

    pass