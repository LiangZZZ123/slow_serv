from collections import UserDict
from typing import Hashable


class Cookie(UserDict):
    def __delitem__(self, key: Hashable) -> None:
        """
        BUG: Here can be a bug: the server does not know the original
        Path and Domain when a cookie-item is generated, so when the server
        wants to delete this cookie-item on the client side, we need to
        manually set Path and Domain to the values which are the same as the
        values when this cookie-item is created.
        
        Here for simplicity, we just assume are cookie-items are created with
        "path:None and domain:None"
        """
        self[key] = CookieItem(key=key, val="", path=None, domain=None, max_age=-1)

    def __setitem__(self, key: Hashable, item) -> None:
        if isinstance(item, CookieItem):
            super().__setitem__(key, item)
        else:
            super().__setitem__(key, CookieItem(key=key, val=item))



class CookieItem:
    """
    Ref of more cookie attributes: 
    https://datatracker.ietf.org/doc/html/rfc6265
    """

    def __init__(
        self, key: Hashable, val, path=None, domain=None, max_age=None
    ) -> None:
        self.key = key
        self.val = val
        self.path = path
        self.domain = domain
        self.max_age = max_age

    def __repr__(self) -> str:
        return str(vars(self))