from slow_serv.resp.cookie import Cookie, CookieItem
from typing import Dict, Hashable, List

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
        self.body: str = """
        <html>
            <title>Default Title</title>
            <body>
                <div>Default Text</div>
            </body>
        </html>"""
        self.content_type: str = "text/html"
        self.content_disposition: str = ""
        self.location: str = ""

        # self.cookie: Dict[str, Tuple[str, Optional[str], Optional[str], Optional[int]]] = {}
        # self.cookie: Dict[str, str] = {}
        self.cookie: Cookie[Hashable, CookieItem] = Cookie()
        self.secret_cookie: Dict[str, str] = {}
        self.setcookie_array: List[str] = []

    def set_status_code(self, status_code: str, text: str):
        self.status_code = status_code
        self.status_code_text = text

    def cookie_to_setcookie_array(self):
        """
        Add all cookies in response_obj.cookie_dict to response_obj.setcookie_array, 
        get ready for creating response_msg from response_obj.
        """
        for k1, v1 in self.cookie.items():
            string = f"Set-Cookie: {v1.key}={v1.val}"

            cookieitem_attrs = vars(v1)
            for k2, v2 in cookieitem_attrs.items():
                if k2 not in ("key", "val"):
                    if v2:
                        string += f"; {k2}={v2}"
            self.setcookie_array.append(string)

    def set_text(self, text: str):
        self.content_type = "text/plain"
        self.body = text

    def set_html(self, html: str):
        self.content_type = "text/html"
        self.body = html

    def set_css(self, css: str):
        self.content_type = "text/css"
        self.body = css

    def set_js(self, js: str):
        self.content_type = "application/javascript"
        self.body = js

    def transform_file(self, file: str, filename: str):
        self.content_type = "application/octet-stream"
        self.body = file
        self.content_disposition = "attachment; filename=" + filename

