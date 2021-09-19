"""
Ref:
https://stackoverflow.com/questions/49821687/how-to-determine-if-i-received-entire-message-from-recv-calls
https://greenbytes.de/tech/webdav/rfc7230.html#message.body.length
"""
import socket
import slow_serv.config


def recv_by_endtag(the_socket: socket.socket, END_TAG: bytes) -> bytes:
    """
    Receive TCP packets until meeting the END_TAG, discard data after the END_TAG.
    """
    total_data = []
    while True:
        data = the_socket.recv(1024)
        index_END_TAG = data.find(END_TAG)
        # if there is a END_TAG in the incoming packet
        if index_END_TAG != -1:
            total_data.append(data[:index_END_TAG])
            break
        total_data.append(data)

        # Now we need to check if END_TAG was split by the last two packets
        if len(total_data) > 1:
            last_pair = total_data[-2] + total_data[-1]
            index_END_TAG = last_pair.find(END_TAG)
            # If is, concat the last two packets, retaining data before
            # index_END_TAG, and discard the rest data
            if index_END_TAG != -1:
                total_data[-2] = last_pair[:index_END_TAG]
                total_data.pop()
                break

    return b"".join(total_data)


def recv_http_head(the_socket: socket.socket, END_TAG: bytes = b"\r\n\r\n") -> bytes:
    """
    Receive data until the whole HTTP head has been received,
    this func is **different from func_rev_by_endtag** in:
        this func does not discard the data after b"\r\n\r\n".
    """

    total_data = []
    while True:
        # NOTE: The doc is rather unclear about what will return (empty 
        # bytestring or empty string) if the other side close the connection,
        # so for the sake of safety, we use "if not data" to do the judgement.
        data = the_socket.recv(slow_serv.config.BUFFER_SIZE)
        if not data:
            the_socket.close()
            return b""

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

    return b"".join(total_data)
