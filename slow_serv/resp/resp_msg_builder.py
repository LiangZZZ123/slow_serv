import datetime
from slow_serv.resp.resp import Response
import traceback


def msg_customized(response: Response) -> bytes:
    resp_head = (
        f"HTTP/1.1 {response.status_code}, {response.status_code_text}"
        + f"\r\nServer: python/slowserv"
        + f"\r\nConnection: close"
        + f"\r\nContent-Type: {response.content_type}"
    )

    if response.content_disposition:
        resp_head += f"\r\nContent-Disposition: {response.content_disposition}"

    for string in response.setcookie_array:
        resp_head += "\r\n" + string

    if response.location:
        resp_head += f"\r\nLocation: {response.location}"

    return (resp_head + "\r\n\r\n" + response.body).encode()


def msg_404(response: Response) -> bytes:
    resp_head = (
        "HTTP/1.1 404 NOT FOUND"
        + "\r\nServer: python/slowserv"
        + "\r\nConnection: close"
        + "\r\nContent-Type: text/html"
    )

    response.body = "404 NOT FOUND\r\n\r\n"
    return (resp_head + "\r\n\r\n" + response.body).encode()


def msg_500(response: Response) -> bytes:
    resp_head = (
        "HTTP/1.1 500 ERROR"
        + "\r\nServer: python/slowserv"
        + "\r\nConnection: close"
        + "\r\nContent-Type: text/html"
    )

    response.body = "500 ERROR\r\n\r\n"
    return (resp_head + "\r\n\r\n" + response.body).encode()
