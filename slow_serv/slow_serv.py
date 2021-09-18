# My server is based on this project: https://github.com/littlefish12345/simpwebserv
# __original_author__ = ["little_fish12345"]

from slow_serv.resp.resp import Response
from slow_serv.resp.msg_builder import msg_from_string, msg_from_response_obj
from typing import Callable, Dict, Tuple, NamedTuple, Union
from urllib import parse
import threading
import traceback
import datetime
import socket
from slow_serv import config


class Server:
    def __init__(self):
        """
        self.endpoint_view_map: a dict that record endpoint-to-viewFunction mappings.
        eg: ('/', "GET") -> main_view

        self.requests_control_map: a dict that record what args parsed from the
        raw http message can be used by current endpoint
        eg: ('/', "GET") -> args_tuple
        """
        self.endpoint_to_view_map = {}
        self.request_control_map = {}

    def route(
        self,
        path: str,
        view_fn: Callable,
        accept_methods=["GET"],  # Ensure "func" and "path" are mandatory
        *,  # Ensure args below must be keyword-arg
        if_build_request=True,  # If wanna build a dict that contains following
        # "request message info"s
        if_cookie=True,
        if_url_parameters=True,
        if_post_form=True,
        if_headers=True,
        if_body=True,
        if_method=True,
    ):
        """
        For the developer's convenience, you can register a router with multiple
        accept_method.

        eg: 
        # The code below will generate two k-v pairs in self.routers(a dict):
        # 1. ('/', "GET") -> main_view
        # 2. ('/', "POST") -> main_view
        app.register(main_view, '/', accept_methods=["GET", "POST"])

        """
        for method in accept_methods:
            # NOTE: Register a router "URL -> ViewFunc".
            self.endpoint_to_view_map[(path, method)] = view_fn

            self.request_control_map[(path, method)] = (
                if_build_request,
                if_cookie,
                if_url_parameters,
                if_post_form,
                if_headers,
                if_body,
                if_method,
            )

    class RegisterParameters(NamedTuple):
        ...

    def run(self, port=5000, host="127.0.0.1", debug=False, KeepAlive=False):  # KeepAlive没做好
        def __handle_request__(
            sock: socket.socket, addr: Tuple[str, int], endpoint_to_view_map: Dict, request_control_map: Dict,
        ):
            """
            TODO: 
            1. Delete request_control_map
            2. split __handle_request__ to
                - recv_stream
                - build_request
                - make_response
                - handle_exception
            """
            data = sock.recv(config.BUFFER_SIZE)
            if not data:
                sock.close()
                return

            """
            head = head_start_line + headers
            Ref: https://developer.mozilla.org/en-US/docs/Web/HTTP/Messages
            
            TODO: We assume that we get the full head with the first sock.recv(),
            but this is not the case. So we need a loop-sock.recv() to get the 
            whole head.
            """
            head, body = data.split(b"\r\n\r\n")
            head_start_line, *headers_rows = head.decode().split("\r\n")

            method, url, http_version = head_start_line.split(" ")

            headers = {}
            for row in headers_rows:
                attr, val = row.split(": ")
                headers[attr] = val

            """
            The Content-Length header is mandatory for messages with entity 
            bodies, unless the message is transported using chunked encoding.

            So we have belowing conditions:
            1. a msg without body doesn't need "Content-Length", eg: GET, HEAD
            2. a msg with body, and with "Content-Length"
            3. a msg with body, no "Content-Length", with "Transfer-Encoding: chunked",
            but since this is not going to be 
            """
            # try:
            #     while True:
            #         if len(body) < int(headers["Content-Length"]):
            #             body = body + sock.recv(config.BUFFER_SIZE)
            #         else:
            #             break
            # except KeyError as e:
            #     pass
            if "Content-Length" in headers:
                while True:
                    if len(body) < int(headers["Content-Length"]):
                        body = body + sock.recv(config.BUFFER_SIZE)
                    else:
                        break
            # # TODO: what if no "Content-Length" in the header?
            elif "chunked" in headers.get("Transfer-Encoding", ""):
                print("`Transfer-Encoding: chunked` not supported on this server")
            elif method in ("GET", "HEAD"):
                pass
            else:
                print("error")

            # Parse the cookie data
            # By convention, we use "cookie" rather than "cookies" as the hashmap name
            cookie = {}
            if "Cookie" in headers:
                cookie_array = headers["Cookie"].split("; ")
                for pair in cookie_array:
                    k, v = pair.split("=")
                    cookie[k] = v

            # Deal with Parameters in GET's URL
            url_parameters = {}
            if (method == "GET" or method == "HEAD") and len(url.split("?")) >= 2:
                url_parameter_array = url.split("?")[-1].split("&")
                for pair in url_parameter_array:
                    k, v = pair.split("=")
                    url_parameters[parse.unquote(k)] = parse.unquote(v)

                # get the url without parameters
                url = "?".join(url.split("?")[0:-1])

            post_form = {}
            if method == "POST":
                # Ref: https://greenbytes.de/tech/webdav/rfc2616.html#rfc.section.14.17
                (content_type,) = headers["Content-Type"].split("; ")

                if "application/x-www-form-urlencoded" in content_type:
                    # If post body is data of k-v tuples
                    # eg: MyVariableOne=ValueOne&MyVariableTwo=ValueTwo
                    # Ref: https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/POST
                    post_form_array = body.decode().split("&")
                    for pair in post_form_array:
                        k, v = pair.split("=")
                        post_form[k] = v

                # TODO: how to deal with data from file?
                if "multipart/form-data" in content_type:
                    pass

            try:
                # BUG: "request" should not be a single dict, it should be two
                # dicts, one is Dict[str, Dict], the other is Dict[str, str], so
                # they can represent all data types parsed from a http message.
                request: Dict[str, Union[Dict[str, str], str]] = {}
                response: Union[str, Response]
                if request_control_map[(url, method)][0] is True:

                    if request_control_map[(url, method)][1]:
                        request["cookie"] = cookie

                    if request_control_map[(url, method)][2]:
                        request["url_parameters"] = url_parameters

                    if request_control_map[(url, method)][3]:
                        request["post_form"] = post_form

                    if request_control_map[(url, method)][4]:
                        request["headers"] = headers

                    if request_control_map[(url, method)][5]:
                        request["body"] = body.decode()

                    if request_control_map[(url, method)][6]:
                        if method == "HEAD":
                            request["method"] = "GET"
                        else:
                            request["method"] = method

                    if method == "HEAD":
                        # NOTE: since we will call view_fn by "view_fn(request)",
                        # so we need to create view_fn by:
                        # def view_fn_1(req):
                        #     pass
                        response = endpoint_to_view_map[(url, "GET")](request)
                    else:
                        response = endpoint_to_view_map[(url, method)](request)
                # Or you can explicit(in this view_fn) refuse to receive any
                # data from request message.
                else:
                    if method == "HEAD":
                        response = endpoint_to_view_map[(url, "GET")]()
                    else:
                        response = endpoint_to_view_map[(url, method)]()

                if isinstance(response, str):
                    msg = msg_from_string(response)
                    # sock.send(
                    #     (
                    #         "HTTP/1.1 200 OK\r\nServer: python/slowserv\r\nContent-Type: text/html\r\nExpires: "
                    #         + datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
                    #         + "\r\nConnection: close\r\n\r\n"
                    #         + response
                    #     ).encode()
                    # )
                    sock.sendall(msg)
                    sock.close()
                    status_code = "200"
                else:
                    # status_code = response.status_code
                    # resp_head = (
                    #     "HTTP/1.1 "
                    #     + status_code
                    #     + " "
                    #     + response.status_code_text
                    #     + "\r\nServer: python/slowserv\r\nConnection: close\r\nContent-Type: "
                    #     + response.content_type
                    #     + "\r\n"
                    # )
                    # if response.content_disposition != None:
                    #     resp_head = resp_head + "Content-Disposition: " + response.content_disposition + "\r\n"
                    # if response.cookie != None:
                    #     for pair in response.cookie:
                    #         resp_head = resp_head + pair + "\r\n"
                    # if response.location != None:
                    #     resp_head = resp_head + "Location: " + response.location + "\r\n\r\n"
                    # resp_head = resp_head + "\r\n"
                    # sock.send(resp_head.encode() + response.body)
                    msg = msg_from_response_obj(response)
                    sock.sendall(msg)
                    sock.close()
            # except KeyError as e:
            #     sock.send(
            #         (
            #             "HTTP/1.1 404 NOT FOUND\r\nServer: python/slowserv\r\nContent-Type: text/html\r\nExpires: "
            #             + datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
            #             + "\r\nConnection: close\r\n\r\n404 NOT FOUND"
            #         ).encode()
            #     )
            #     sock.close()
            #     status_code = "404"
            except Exception as e:
                if debug:
                    sock.send(
                        (
                            "HTTP/1.1 500 ERROR\r\nServer: python/slowserv\r\nContent-Type: text/html\r\nExpires: "
                            + datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
                            + "\r\nConnection: close\r\n\r\n500 error\r\n\r\nlog:\r\n"
                            + traceback.format_exc()
                        ).encode()
                    )
                else:
                    sock.send(
                        (
                            "HTTP/1.1 500 ERROR\r\nServer: python/slowserv\r\nContent-Type: text/html\r\nExpires: "
                            + datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
                            + "\r\nConnection: close\r\n\r\n500 error"
                        ).encode()
                    )
                sock.close()
                status_code = "500"
            print(method + " " + url + " " + status_code + " " + addr[0])

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((host, port))
        sock.listen(5)
        print("Server is running on http://" + host + ":" + str(port))
        while True:
            fd, addr = sock.accept()
            t = threading.Thread(
                target=__handle_request__, args=(fd, addr, self.endpoint_to_view_map, self.request_control_map,),
            )
            t.start()
