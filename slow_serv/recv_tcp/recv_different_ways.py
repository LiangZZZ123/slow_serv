import socket, struct, sys, time


def recv_basic(the_socket:socket.socket)->bytes:
    total_data = []
    while 1:
        data = the_socket.recv(1024)
        if not data:
            break
        total_data.append(data)
    return b"".join(total_data)


def recv_by_timeout(the_socket:socket.socket, timeout=1)->bytes:
    # set the socket to nonblocking, which means if s.recv doesn't get anything,
    # raise socket.timeout immediately
    the_socket.setblocking(False)
    total_data = []
    start_time = time.perf_counter()
    while 1:
        cur_time = time.perf_counter()
        # break the recv after wating for "timeout" seconds
        if cur_time - start_time > timeout:
            break
        try:
            data = the_socket.recv(1024)
            if data:
                total_data.append(data)
                start_time = time.perf_counter()
            else:
                time.sleep(0)
        except (socket.timeout, socket.error) as e:
            print(e)
            pass

    return b"".join(total_data)


END_TAG = b"\r\n\r\nsecret end"


def recv_by_endtag(the_socket: socket.socket)->bytes:
    total_data = []
    # data = ''
    while True:
        data = the_socket.recv(1024)
        index_END_TAG = data.find(END_TAG)
        # if there is a END_TAG in the incoming packet
        if index_END_TAG != -1:
            total_data.append(data[:index_END_TAG])
            break

        # Now we need to check if END_TAG was split by the last two packets
        if len(total_data) > 1:
            last_pair = total_data[-2] + total_data[-1]
            index_END_TAG = last_pair.find(END_TAG)
            # If is, concat the last two packets, retaining data before
            # index_END_TAG, and discard the rest data
            if index_END_TAG != 1:
                total_data[-2] = last_pair[:index_END_TAG]
                total_data.pop()
                break

    return b"".join(total_data)

