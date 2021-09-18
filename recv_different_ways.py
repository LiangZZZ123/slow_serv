import socket, struct, sys, time


def recv_basic(the_socket):
    total_data = []
    while 1:
        data = the_socket.recv(1024)
        if not data:
            break
        total_data.append(data)
    return "".join(total_data)


def recv_by_timeout(s, timeout=1):
    # set the socket to nonblocking, which means if s.recv doesn't get anything,
    # raise socket.timeout immediately
    s.setblocking(False)
    total_data = []
    start_time = time.perf_counter()
    while 1:
        cur_time = time.perf_counter()
        # break the recv after wating for "timeout" seconds
        if cur_time - start_time > timeout:
            break
        try:
            data = s.recv(1024)
            if data:
                total_data.append(data)
                start_time = time.perf_counter()
            else:
                time.sleep(0.1)
        except (socket.timeout, socket.error) as e:
            print(e)
            pass

    return "".join(total_data)


END_TAG = "\r\n\r\nsecret end"


def recv_by_endtag(the_socket):
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

        return "".join(total_data)


def recv_size(the_socket):
    # data length is packed into 4 bytes
    total_len = 0
    total_data = []
    size = sys.maxint
    size_data = sock_data = ""
    recv_size = 8192
    while total_len < size:
        sock_data = the_socket.recv(recv_size)
        if not total_data:
            if len(sock_data) > 4:
                size_data += sock_data
                # Get "size" from data packet
                size = struct.unpack(">i", size_data[:4])[0]
                recv_size = size
                if recv_size > 524288:
                    recv_size = 524288
                total_data.append(size_data[4:])
            else:
                size_data += sock_data
        else:
            total_data.append(sock_data)
        total_len = sum([len(i) for i in total_data])
    return "".join(total_data)

