from re import sub
import subprocess
import pytest
import os
import signal
import time

"""
I cannot figure out why I cannot create a process running web server during
test in this way, now just skip it and test by manually starting the webserver.
"""

# BUG: Why this doesn't work ?
# @pytest.fixture(scope="session")
# def start_server():
#     p = subprocess.Popen("python app.py", shell=True, preexec_fn=os.setsid)
#     time.sleep(1)
#     assert p
#     yield
#     # os.killpg(p.pid, signal.SIGTERM)
#     p.terminate()


# def test(start_server):
def test_main_get():
    # "-v" in curl shows the HTTP request headers, among response process
    # normally when we use "-v", we don't need "-i", because the response is already included
    _, output = subprocess.getstatusoutput("curl localhost:5000?city=Ning%20Bo -v -s")

    assert "Content-Type: text/plain" in output
    assert "Received a GET, with URL parameters: {'city': 'Ning Bo'}" in output


def test_main_post():
    _, output = subprocess.getstatusoutput(
        "curl localhost:5000 -d 'city=Ning Bo' -i -s"
    )
    assert "Content-Type: text/plain" in output
    assert "Received a POST, with post form: {'city': 'Ning Bo'}" in output


def test_fake_baidu_get():
    _, output = subprocess.getstatusoutput("curl localhost:5000/fake_baidu -i -s")
    assert "Content-Type: text/html" in output
    assert "百度一下，你就知道" in output


def test_modify_cookie_get():
    _, output = subprocess.getstatusoutput(
        "curl --cookie 'k1=v1;k2=v2' localhost:5000/modify_cookie -i -s"
    )

    assert "Set-Cookie: k1=kkk\nSet-Cookie: k2=kkk\n" in output


def test_add_cookie_get():
    _, output = subprocess.getstatusoutput(
        "curl --cookie 'k1=v1;k2=v2' localhost:5000/add_cookie -i -s"
    )
    assert "Set-Cookie: c1=1\nSet-Cookie: c2=2\nSet-Cookie: c3=3\n" in output


def test_download_file_get():
    _, output = subprocess.getstatusoutput("curl localhost:5000/download_file -i -s")
    assert "Content-Type: application/octet-stream" in output


def test_encrypt_cookie():
    ...


def test_show_encrypt_cookie():
    ...
