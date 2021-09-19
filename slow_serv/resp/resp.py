from typing import Dict, IO, List, Optional
from urllib import parse
from slow_serv import config

# __all__ = ["Response"]


class Response:
    """
    In every view_fn, you should either:
    1. create a Response instance and return it;
    2. return a string, as the body of response message. 
    """

    def __init__(self):
        self.status_code: str = "200"
        self.status_code_text: str = "OK"
        self.body: bytes = b"<html><head>This is a blank page</head></html>"
        self.content_type: str = "text/html"
        self.content_disposition: str = ""
        self.cookie: List[str] = []
        self.location: str = ""

    def set_status_code(self, status_code: str, text: str):
        self.status_code = status_code
        self.status_code_text = text

    def add_cookie(
        self, key: str, value: str, path: Optional[str] = None, domain: Optional[str] = None, max_age: Optional[int] = None
    ):
        set_cookie_text = "Set-Cookie: " + parse.quote(key) + "=" + parse.quote(value)
        print(set_cookie_text)
        if path:
            set_cookie_text += "; Path=" + path
        if domain:
            set_cookie_text += "; Domain=" + domain
        if max_age:
            set_cookie_text += "Max-Age=" + str(max_age)

        self.cookie.append(set_cookie_text)

    def del_cookie(self, key: str, path: Optional[str] = None, domain: Optional[str] = None):  # 键  # 指定路径  # 指定域名
        set_cookie_text = "Set-Cookie: " + parse.quote(key) + "=" + ""
        set_cookie_text += "; Max-Age=-1"

        if path:
            set_cookie_text += "; Path=" + path
        if domain:
            set_cookie_text += "; Domain=" + domain
        self.cookie.append(set_cookie_text)

    # def add_cookie_bulk(self, hashmap:Dict[str, str], do_secret_cookie=config.DO_SECRET_COOKIE):
    #     ...

    def set_text(self, text: str):
        self.content_type = "text/plain"
        self.body = text.encode()

    def set_html(self, html: str):
        self.content_type = "text/html"
        self.body = html.encode()

    def set_css(self, css: str):
        self.content_type = "text/css"
        self.body = css.encode()

    def set_js(self, js: str):
        self.content_type = "application/javascript"
        self.body = js.encode()

    def transform_file(self, file: bytes, filename: str):
        self.content_type = "application/octet-stream"
        self.body = file
        self.content_disposition = "attachment; filename=" + filename

