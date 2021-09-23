from typing import Dict, Optional


class Request:
    def __init__(
        self,
        method: str,
        headers: Dict[str, str],
        url_parameters: Optional[Dict[str, str]] = None,
        cookie: Optional[Dict[str, str]] = None,
        post_form: Optional[Dict[str, str]] = None,
        body: Optional[str] = None,
    ):

        self.method = method
        self.headers = headers

        self.url_parameters = {} if not url_parameters else url_parameters
        self.cookie = {} if not cookie else cookie
        self.post_form = {} if not post_form else post_form
        self.body = "" if not body else body
