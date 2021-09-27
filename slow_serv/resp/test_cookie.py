from slow_serv.resp.cookie import Cookie, CookieItem
from pprint import pprint


def test_cookie_and_cookieitem():
    c = Cookie({1: 1, 2: 2})

    # test __setitem__
    for k, v in c.items():
        assert isinstance(v, CookieItem)

    assert c[1].val == 1
    assert c[1].path == None

    # test __delitem__
    del c[1]
    assert c[1].val == ""
    assert c[1].max_age == -1
    # pprint(c)
