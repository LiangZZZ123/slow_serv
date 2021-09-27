"""
The basic way of creating an web application with slow_serv is:

app = slow_serv.Server()
def main(request, response):
    response.body="BIG APP supported by slow_serv"
app.route("/", main)
app.run()


Here are some web pages created using slow_serv that you can play with.

You can play with them either entering URL using a web browser or using command
line(eg: curl). 

I've included some command line script in `test_app_slow_serv.py`, running
those scripts manually will give you a better understing of how slow_serv can
work!
"""

import logging
from typing import Dict, List, TypeVar, Union

from slow_serv import slow_serv
from slow_serv.resp.resp import Response
from slow_serv.req.req import Request
from slow_serv.hooks.hook_secret_cookie import cipher, decipher


def main(request: Request, response: Response) -> Response:
    if request.method == "GET":
        data = f"Received a GET, with URL parameters: {request.url_parameters}"
    elif request.method == "POST":
        data = f"Received a POST, with post form: {request.post_form}"

    response.set_text(data)

    return response


def fake_baidu(request: Request, response: Response) -> Response:
    with open("./static_files/fake_baidu.html") as f:
        data = f.read()

    response.set_html(data)
    return response


def download_file(request: Request, response: Response) -> Response:
    filename = "./static_files/amazing_file.txt"
    with open(filename, "rb") as f:
        response.transform_file(f.read().decode(), filename)
    return response


def add_cookie(request: Request, response: Response) -> Response:
    response.cookie["c1"] = "1"
    response.cookie["c2"] = "2"
    response.cookie["c3"] = "3"

    return response


def modify_cookie(request: Request, response: Response) -> Response:
    for k, v in request.cookie.items():
        response.cookie[k] = "kkk"

    return response


def add_secret_cookie_using_url_parameter(
    request: Request, response: Response
) -> Response:

    response.cookie['name'] = "Leo"

    for k, v in request.url_parameters.items():
        response.secret_cookie[k] = v

    array: List[str] = []
    for k, v in response.secret_cookie.items():
        array.append(f"<tr><td>{k}</td><td>{v}</td></tr>")

    kv_str = "".join(array)
    response.body = f"<table><tr><td>secret_cookie_key</td><td>secret_cookie_val</td></tr>{kv_str}</table>"

    return response


app = slow_serv.Server()
# NOTE: We need "/" for the main page because it is the default file under our
# top level domain
app.route("/", main, methods=["GET", "POST"])
# "/" and "/fake_baidu" are on the same levels in our file structure
app.route("/fake_baidu", fake_baidu, methods=["GET", "POST"])

app.route("/download_file", download_file)

app.route("/add_cookie", add_cookie, methods=["GET"])
app.route("/modify_cookie", modify_cookie, methods=["GET"])
app.route(
    "/add_secret_cookie_using_url_parameter",
    add_secret_cookie_using_url_parameter,
    methods=["GET"],
)


if __name__ == "__main__":
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
    # logging.basicConfig(filename='my.log', level=logging.DEBUG, format=LOG_FORMAT, datefmt=DATE_FORMAT)
    # app.run(debug=True)
    logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT, datefmt=DATE_FORMAT)
    app.run(port=5000, host="localhost", debug=True)
