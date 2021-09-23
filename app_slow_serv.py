import logging
from typing import Dict, TypeVar, Union
from slow_serv import slow_serv
from slow_serv.resp.resp import Response
from slow_serv.req.req import Request
from slow_serv.secret_cookie import encrypt, decrypt
import json
import config


def main(request: Request, response: Response) -> Response:
    if request.method == "GET":
        data = f"Received a GET, with URL parameters: {request.url_parameters}"
    elif request.method == "POST":
        data = f"Received a POST, with post form: {request.post_form}"

    response.set_text(data)
    response.content_type = "text/plain"
    
    return response


def fake_baidu(request: Request, response: Response) -> Response:
    with open("./static_files/fake_baidu.html") as f:
        data = f.read()

    response.set_html(data)
    return response


def modify_cookie(request: Request, response: Response) -> Response:
    for k, v in request.cookie.items():
        response.add_cookie(k, "kkk")

    return response

def add_cookie(request: Request, response: Response) -> Response:
    response.add_cookie('c1', "1")
    response.add_cookie('c2', "2")
    response.add_cookie('c3', "3")

    return response



def download_file(request: Request, response: Response) -> Response:
    filename = "./static_files/amazing_file.txt"
    with open(filename, "rb") as f:
        response.transform_file(f.read().decode(), filename)
    return response


def encrypt_cookie(request: Request, response: Response) -> Response:

    if not request.cookie:
        request.cookie = {"1": "aa", "2": "bb", "3": "cc"}

    cookie_str = json.dumps(request.cookie)
    ciphertext, nonce = encrypt(cookie_str, config.SECRET_KEY)
    response.add_cookie("encrypt_cookie", ciphertext.decode())
    response.add_cookie("nonce", nonce.decode())

    return response


def show_encrypt_cookie(request: Request, response: Response) -> Response:

    if "nonce" not in request.cookie and "encrypt_cookie" not in request.cookie:
        response.body = "Your cookie is not encrypted"

    ciphertext = request.cookie["encrypt_cookie"].encode()
    nonce = request.cookie["nonce"].encode()
    cookie_str = decrypt(ciphertext, config.SECRET_KEY, nonce)

    if not cookie_str:
        response.body = "Your encrypt-cookie has been tempered !!!"
    else:
        for k, v in request.cookie.items():
            response.add_cookie(k, v)
        response.body = "We cannot show you what's inside the secret-cookie"
    return response


app = slow_serv.Server()
# NOTE: We need "/" for the main page because it is the default file under our
# top level domain
app.route("/", main, methods=["GET", "POST"])
# "/" and "/fake_baidu" are on the same levels in our file structure
app.route("/fake_baidu", fake_baidu, methods=["GET", "POST"])

app.route("/modify_cookie", modify_cookie, methods=["GET"])
app.route("/add_cookie", add_cookie, methods=["GET"])

app.route("/download_file", download_file)

app.route("/encrypt_cookie", encrypt_cookie)
app.route("/show_encrypt_cookie", show_encrypt_cookie)

if __name__ == "__main__":
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
    # logging.basicConfig(filename='my.log', level=logging.DEBUG, format=LOG_FORMAT, datefmt=DATE_FORMAT)
    # app.run(debug=True)
    logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT, datefmt=DATE_FORMAT)
    app.run(port=5000, host="localhost", debug=True)
