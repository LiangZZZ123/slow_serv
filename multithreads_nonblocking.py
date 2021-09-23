import socket
import logging
import sys
from contextlib import suppress

BUFFER_SIZE = 1024

def non_blocking_server(port, hostname='localhost'):
    try:
        sockfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as e:
        logging.critical(e)
        logging.critical('Could not open socket. Exiting.')
        sys.exit(1)

    try:
        sockfd.bind((hostname, port))
        sockfd.listen(10)
        sockfd.setblocking(False)
    except socket.error as e:
        logging.critical(e)
        logging.critical('Could not start up server. Exiting.')
        sockfd.close()
        sys.exit(2)

    connected = {}
    receiving = {}
    sending = {}
    while True:
        with suppress(BlockingIOError):
            client, client_addr = sockfd.accept()
            logging.info('Connection from client {!r}'.format(client_addr))
            connected[client] = client_addr
            receiving[client] = b''

        still_receiving = {}
        for client, data in receiving.items():
            try:
                buf = client.recv(BUFFER_SIZE)
                if buf:
                    still_receiving[client] = data + buf
                else:
                    logging.info('Client: {} sent {} bytes.'.format(connected[client], len(data)))
                    sending[client] = (memoryview(data), 0)
            except BlockingIOError:
                still_receiving[client] = data
        receiving = still_receiving

        still_sending = {}
        for client, (message, sent_bytes) in sending.items():
            try:
                sent = client.send(message[sent_bytes:])
                sent_bytes += sent

                if sent:
                    still_sending[client] = (message, sent_bytes)
                else:
                    logging.info('Server sent {} bytes to client: {!r}'.format(sent_bytes, connected[client]))
                    client.close()
                    del connected[client]
            except BlockingIOError:
                still_sending[client] = (message, sent_bytes)
            except ConnectionResetError:
                # in case client disconnected before we send the echo
                logging.info('Client {!r} disconnected before sending echo.'.format(connected[client]))
                logging.info('Server sent {} bytes to client: {!r}'.format(sent_bytes, connected[client]))
                client.close()
                del connected[client]
        sending = still_sending

if __name__ == "__main__":
    non_blocking_server(5000)