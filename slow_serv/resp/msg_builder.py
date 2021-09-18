import datetime
from slow_serv.resp.resp import Response


def msg_from_string(response: str) -> bytes:
    msg = (
        "HTTP/1.1 200 OK\r\nServer: python/slowserv\r\nContent-Type: text/html\r\nExpires: "
        + datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
        + "\r\nConnection: close\r\n\r\n"
        + response
    ).encode()

    return msg


def msg_from_response_obj(response: Response) -> bytes:
    status_code = response.status_code
    resp_head = (
        "HTTP/1.1 "
        + status_code
        + " "
        + response.status_code_text
        + "\r\nServer: python/slowserv\r\nConnection: close\r\nContent-Type: "
        + response.content_type
        + "\r\n"
    )
    if response.content_disposition != None:
        resp_head = resp_head + "Content-Disposition: " + response.content_disposition + "\r\n"

    if response.cookie != None:
        for pair in response.cookie:
            resp_head = resp_head + pair + "\r\n"

    if response.location != None:
        resp_head = resp_head + "Location: " + response.location + "\r\n\r\n"
    resp_head = resp_head + "\r\n"

    return resp_head.encode() + response.body
