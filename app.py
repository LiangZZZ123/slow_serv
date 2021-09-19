from typing import Dict, TypeVar, Union
from slow_serv import slow_serv
from slow_serv.resp.resp import Response
from slow_serv.secret_cookie import do_encrypt, de_encrypt
import json
import config


def main(request: Dict[str, Union[Dict[str, str], str]]) -> Union[str, Response]:
    resp = Response()
    if request["method"] == "GET":
        data = f"Received a GET, with URL parameters: {request['url_parameters']}"
    elif request["method"] == "POST":
        data = f"Received a POST, with post form: {request['post_form']}"

    resp.set_text(data)
    # resp.content_type = "text/plain"
    return resp


def fake_baidu(request: Dict[str, Union[Dict[str, str], str]]) -> Union[str, Response]:
    resp = Response()

    with open("./static_files/fake_baidu.html") as f:
        data = f.read()

    resp.set_html(data)
    return resp


def modify_cookie(request: Dict[str, Union[Dict[str, str], str]]) -> Union[str, Response]:
    resp = Response()

    # print(request["cookie"])
    for k, v in request["cookie"].items():
        resp.add_cookie(k, "hahaha, things are mixed up!")

    return resp


def download_file(request: Dict[str, Union[Dict[str, str], str]]) -> Union[str, Response]:
    resp = Response()
    filename = "./static_files/amazing_file.txt"
    with open(filename, "rb") as f:
        resp.transform_file(f.read(), filename)
    return resp


def encrypt_cookie(request: Dict[str, Union[Dict[str, str], str]]) -> Union[str, Response]:
    resp = Response()

    if not request["cookie"]:
        request["cookie"] = {"1": "aa", "2": "bb", "3": "cc"}

    cookie_str = json.dumps(request["cookie"])
    ciphertext, nonce = do_encrypt(cookie_str, config.SECRET_KEY)
    resp.add_cookie("encrypt_cookie", ciphertext.decode())
    resp.add_cookie("nonce", nonce.decode())

    return resp


def show_encrypt_cookie(request: Dict[str, Union[Dict[str, str], str]]) -> Union[str, Response]:

    if "nonce" not in request["cookie"] and "encrypt_cookie" not in request["cookie"]:
        return "Your cookie is not encrypted"

    ciphertext = request["cookie"]["encrypt_cookie"].encode()
    nonce = request["cookie"]["nonce"].encode()
    cookie_str = de_encrypt(ciphertext, config.SECRET_KEY, nonce)

    if not cookie_str:
        return "Your encrypt-cookie has been tempered !!!"
    else:
        resp = Response()
        for k, v in request["cookie"].items():
            resp.add_cookie(k, v)
        resp.body = b"We cannot show you what's inside the secret-cookie"
        return resp


app = slow_serv.Server()
# NOTE: We need "/" for the main page because it is the default file under our
# top level domain
app.route("/", main, accept_methods=["GET", "POST"])
# "/" and "/fake_baidu" are on the same levels in our file structure
app.route("/fake_baidu", fake_baidu, accept_methods=["GET", "POST"])

app.route("/modify_cookie", modify_cookie, accept_methods=["GET"])

app.route("/download_file", download_file)

app.route("/encrypt_cookie", encrypt_cookie)
app.route("/show_encrypt_cookie", show_encrypt_cookie)

if __name__ == "__main__":
    app.run(debug=True)
