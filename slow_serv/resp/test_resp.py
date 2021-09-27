from slow_serv.resp.cookie import Cookie
from slow_serv.resp.resp import Response


def test_Response():
    resp = Response()
    resp.cookie = Cookie({1: 1, 2: 2})

    resp.cookie[3] = 3
    del resp.cookie[1]

    resp.cookie_to_setcookie_array()
    assert resp.setcookie_array == [
        "Set-Cookie: 1=; max_age=-1",
        "Set-Cookie: 2=2",
        "Set-Cookie: 3=3",
    ]

