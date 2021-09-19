# NOTE: Ref:
# Foundations of Python Network Programming, Third Edition
# https://github.com/brandon-rhodes/fopnp/blob/m/py3/chapter05/blocks.py
# Sending data over a stream but delimited as length-prefixed blocks.

"""
Three indicates for "the end of a message body":

1. For HTTP protocol 1.0 the connection closing was used to signal the end of 
data.

2. This was improved in HTTP 1.1 which supports persistant connections. 
For HTTP 1.1 typically you set or read the Content-Length header to know how 
much data to expect.

3. Finally with HTTP 1.1 there is also the possibility of "Chunked" mode, you 
get the size as they come and you know you've reached the end when the chunk 
"Size == 0" is found.
"""

import socket, struct
from argparse import ArgumentParser

"""
Manually define the whole data packet as 
    struct{
        int header
        rest data
        }

Get the header by reading the first 4-bytes with format "!I"
(big-endian int defined by IETF RFC 1700 ) of the current packet 

So here we define a Struct object with fmt = "!I", this object can writes and 
reads binary data according to the format string fmt.
"""
# header_struct = struct.Struct("!i")


def recvall(sock, length):
    length_not_received = length
    total_data = []
    while length_not_received:
        data = sock.recv(length_not_received)
        if not data:
            raise EOFError(
                "socket closed with {} bytes left to be received".format(
                    length_not_received
                )
            )
        length_not_received -= len(data)
        total_data.append(data)
    return b"".join(total_data)


def get_content(sock):
    """
    Q: Why we do recvall() twice?
    A: Because the second call need "length" parameter, which is the return value
    of the first call.

    struct.Struct("!I").size == 4, which means "len(c_int) == 4 bytes"
    call recvall(sock, length=4) will give us the header_in_binary_data, which
     is the binary-repr of the content_length
    """
    header_in_binary_data = recvall(sock, length=4)
    (content_length,) = struct.unpack("!i", header_in_binary_data)

    return recvall(sock, content_length)


def send_content(sock, data):
    # block_length = len(message)
    # sock.send(header_struct.pack(block_length))
    # sock.send(message)

    # sock.send(struct.pack("!iif", 1, 1, 1.1))
    sock.send(struct.pack("!i", len(data)))
    sock.send(data)


def server(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((ip, port))
    sock.listen(1)
    print('Run this script in another window with "-c" to connect')
    print("Listening at", sock.getsockname())
    sc, sockname = sock.accept()
    print("Accepted connection from", sockname)
    sc.shutdown(socket.SHUT_WR)
    while True:
        data = get_content(sc)
        if not data:
            break
        print("Client side says:", repr(data))
    sc.close()
    sock.close()


def client(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    sock.shutdown(socket.SHUT_RD)
    send_content(sock, b"Beautiful is better than ugly.")
    send_content(sock, b"Explicit is better than implicit.")
    send_content(sock, b"Simple is better than complex.")
    send_content(sock, b"")
    sock.close()


if __name__ == "__main__":
    parser = ArgumentParser(description="Transmit & receive blocks over TCP")
    parser.add_argument(
        "hostname",
        nargs="?",
        default="127.0.0.1",
        help="IP address or hostname (default: %(default)s)",
    )
    parser.add_argument("-c", action="store_true", help="run as the client")
    parser.add_argument(
        "-p",
        type=int,
        metavar="port",
        default=1060,
        help="TCP port number (default: %(default)s)",
    )
    args = parser.parse_args()
    function = client if args.c else server
    function(args.hostname, args.p)
