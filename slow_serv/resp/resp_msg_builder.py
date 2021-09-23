import datetime
from slow_serv.resp.resp import Response
import traceback


def msg_created_with_response_obj(response: Response) -> bytes:
    resp_head = (
        f"HTTP/1.1 {response.status_code}, {response.status_code_text}"
        + f"\r\nServer: python/slowserv"
        + f"\r\nConnection: close"
        + f"\r\nContent-Type: {response.content_type}"
    )

    if response.content_disposition:
        resp_head += f"\r\nContent-Disposition: {response.content_disposition}"

    if response.cookie:
        for pair in response.cookie:
            resp_head += "\r\n" + pair

    if response.location:
        resp_head += f"\r\nLocation: {response.location}"

    return resp_head.encode() + b"\r\n\r\n" + response.body.encode()


def msg_500(response: Response) -> bytes:
    resp_head = (
        "HTTP/1.1 500 ERROR"
        + "\r\nServer: python/slowserv"
        + "\r\nConnection: close"
        + "\r\nContent-Type: text/html"
    )

    response.body = "500 ERROR\r\n\r\nlog:\r" + f"\r\n{traceback.format_exc()}"
    return resp_head.encode() + b"\r\n\r\n" + response.body.encode()
