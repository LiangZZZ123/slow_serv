# My server is based on this project: https://github.com/littlefish12345/simpwebserv
# __original_author__ = ["little_fish12345"]

from typing import Any, Callable, Dict, Tuple, NamedTuple, Union
from urllib import parse
import threading
import traceback
import datetime
import socket
import time
import logging

from slow_serv.resp.resp import Response
from slow_serv.req.req import Request
from slow_serv.resp.resp_msg_builder import msg_created_with_response_obj
from slow_serv import config
from slow_serv.recv_tcp.recv_tcp_framing import recv_http_head


class Server:
    run_options: Dict[str, Any] = {}

    def __init__(self):
        """
        self.endpoint_view_map: a dict that record endpoint-to-viewFunction 
        mappings.
        eg: ('/', "GET") -> main_view
        """
        self.endpoint_to_view_map = {}

    def route(self, path: str, view_fn: Callable, methods=["GET"]):
        """
        For the developer's convenience, you can register a router with multiple
        accept_method.

        eg: 
        # The code below will generate two k-v pairs in self.routers(a dict):
        # 1. ('/', "GET") -> main_view
        # 2. ('/', "POST") -> main_view
        app.register(main_view, '/', accept_methods=["GET", "POST"])

        """
        for method in methods:
            # Register a router "(URL, method) -> ViewFunc".
            self.endpoint_to_view_map[(path, method)] = view_fn

    def run(self, port=5000, host="127.0.0.1", debug=False):
        config.DEBUG = debug

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((host, port))
        sock.listen(100)

        logging.info("Server is running on http://" + host + ":" + str(port))
        while True:
            fd, addr = sock.accept()
            """
            Here, "sock" is monitoring the (IP, port), it's blocking, but
            its OK. "sock" is waiting for the first fd(A successful TCP
            handshake) to comes in.
            All in all, "listening-socket" can be blocking, but "fd-socket"
            should not be blocking!
            
            **Why use nonblocking fd**:
                If "fd" is blocking, and the packet for this "fd" in system-tcp-cache is not 
            ready, then "While True: data = fd.recv()" may be blocked during the while CPU
            time slice allocated to this thread. 
                So a better choice is using nonblocking fd, "fd.recv()" would immediately 
            raise "errno.EWOULDBLOCK or errno.EAGAIN" if no packet are available in system-
            tcp-cache. Then in handling-exception you just call "time.sleep(0)" to switch 
            the thread.

            There are three ways to set a fd to nonblocking in Python, each
            will give a different exception if no data is available when
            "fd.recv()" is called.
            Ref: https://stackoverflow.com/questions/16745409/what-does-pythons-socket-recv-return-for-non-blocking-sockets-if-no-data-is-r
            """
            t = threading.Thread(
                target=self.handle_request, args=(fd, addr, self.endpoint_to_view_map),
            )
            t.start()

    # TODO: KeepAlive
    def handle_request(
        self,
        fd: socket.socket,
        addr: Tuple[str, int],
        endpoint_to_view_map: Dict,
        KeepAlive: bool = False,
    ):
        """
            Read and parse the incoming data.

            TODO: 
            1. split handle_request to
                - recv_stream
                - build_request
                - make_response
                - handle_exception
            """
        # HACK: Why cannot we do multithreads + nonblocking-socket + sleep() here,
        # this really confuses me!
        # fd.setblocking(False)

        total_data = []
        END_TAG = b"\r\n\r\n"
        count = 0
        while True:
            try:
                data = fd.recv(config.BUFFER_SIZE)
                # NOTE: The doc is rather unclear about what will return (empty
                # bytestring or empty string) if the other side close the connection,
                # so for the sake of safety, we use "if not data" to do the judgement.
                if not data:
                    return

                total_data.append(data)

                index_END_TAG = data.find(END_TAG)
                # if there is a END_TAG in the incoming packet
                if index_END_TAG != -1:
                    break

                # Now we need to check if END_TAG was split by the last two packets
                if len(total_data) > 1:
                    last_pair = total_data[-2] + total_data[-1]
                    index_END_TAG = last_pair.find(END_TAG)
                    if index_END_TAG != -1:
                        break

            # except BlockingIOError as e:
            # logging.debug(str(e) + "| no data on http-head received, wait a bit longer")
            #     time.sleep(1)
            #     continue
            except socket.error as e:
                logging.error(str(e) + "| error during receiving http head")
                return

        data = b"".join(total_data)

        # data = recv_http_head(sock)
        # # If no data received, that means the other side has closed the
        # # connection.
        # if not data:
        #     return

        # head = head_start_line + headers
        # Ref: https://developer.mozilla.org/en-US/docs/Web/HTTP/Messages
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
            3. a msg with body, no "Content-Length", with "Transfer-Encoding: chunked"
            """
        if "Content-Length" in headers:
            body_in_array = [body]
            body_length = len(body)
            # BUG: This while loop can block
            # https://stackoverflow.com/questions/16745409/what-does-pythons-socket-recv-return-for-non-blocking-sockets-if-no-data-is-r
            while True:
                # It's possible that "head and body" is received in one
                # bucket, so do the length-check first.
                if body_length >= int(headers["Content-Length"]):
                    break

                try:
                    body_continue = fd.recv(config.BUFFER_SIZE)

                    # If the other side shutdown the connect
                    if not body_continue:
                        return

                    body_length += len(body_continue)
                    body_in_array.append(body_continue)
                # except BlockingIOError as e:
                # logging.info(str(e) + "| no data on http-body received, wait wait")
                #     time.sleep(0)
                #     continue
                except socket.error as e:
                    logging.error(str(e) + "| error during receiving http body")
                    return

            body = b"".join(body_in_array)

        # TODO: a msg with body, no "Content-Length", with "Transfer-Encoding: chunked"
        elif "chunked" in headers.get("Transfer-Encoding", ""):
            logging.warning("`Transfer-Encoding: chunked` not supported on this server")
            return
        elif method in ("GET", "HEAD"):
            pass
        else:
            logging.info("Cannot parse the http request")
            return

        # Parse the cookie data
        # By convention, we use "cookie" rather than "cookies" as the hashmap name
        cookie = {}
        if "Cookie" in headers:
            cookie_array = headers["Cookie"].split(";")
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
            # BUG: mypy gives error on current "request"'s structure,
            # "request" should not be a single dict, it should be two
            # dicts, one is Dict[str, Dict], the other is Dict[str, str], so
            # they can represent all data types parsed from a http message.

            method = "GET" if method == "HEAD" else method

            request = Request(
                method, headers, url_parameters, cookie, post_form, body.decode()
            )
            response = Response()

            # for hook in config.BEFOR_ROUTE_HOOKS:

            # NOTE: since we will call view_fn by "view_fn(request)",
            # so we need to create view_fn by:
            # def view_fn_1(req):
            #     pass

            endpoint_to_view_map[(url, request.method)](request, response)

            msg = msg_created_with_response_obj(response)
            fd.sendall(msg)
            fd.close()
            status_code = "200"

        # except KeyError as e:
        #     fd.send(
        #         (
        #             "HTTP/1.1 404 NOT FOUND\r\nServer: python/slowserv\r\nContent-Type: text/html\r\nExpires: "
        #             + datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
        #             + "\r\nConnection: close\r\n\r\n404 NOT FOUND"
        #         ).encode()
        #     )
        #     fd.close()
        #     status_code = "404"
        except Exception as e:
            if config.DEBUG is True:
                fd.send(
                    (
                        "HTTP/1.1 500 ERROR\r\nServer: python/slowserv\r\nContent-Type: text/html\r\nExpires: "
                        + datetime.datetime.utcnow().strftime(
                            "%a, %d %b %Y %H:%M:%S GMT"
                        )
                        + "\r\nConnection: close\r\n\r\n500 ERROR\r\n\r\nlog:\r\n"
                        + traceback.format_exc()
                    ).encode()
                )
            else:
                fd.send(
                    (
                        "HTTP/1.1 500 ERROR\r\nServer: python/slowserv\r\nContent-Type: text/html\r\nExpires: "
                        + datetime.datetime.utcnow().strftime(
                            "%a, %d %b %Y %H:%M:%S GMT"
                        )
                        + "\r\nConnection: close\r\n\r\n500 ERROR"
                    ).encode()
                )
            fd.close()
            status_code = "500"
        logging.info(
            method
            + " "
            + url
            + " "
            + status_code
            + " "
            + addr[0]
            # + f"; threading ID: {threading.get_ident()}"
        )

