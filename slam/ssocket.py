import logging
import socket
import time


class Socket():
    def __init__(self, host, port):
        logging.info(f"Establishing a socket to {host}:{port}")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        connected = False
        while not connected:
            try:
                self.sock.connect((host, port))
                connected = True
            except OSError:
                time.sleep(1)
        self.recv_buffer = b""
        logging.info(f"Socket to {host}:{port} established")

    def send(self, message: str, end_char=b"\0"):
        total = 0
        msg = message.encode() + end_char
        while total < len(msg):
            sent = self.sock.send(msg[total:])
            if sent == 0:
                raise BrokenPipeError("Socket connection broken")
            total += sent

    def receive(self, end_char=b"\0"):
        while end_char not in self.recv_buffer:
            try:
                chunk = self.sock.recv(1024)
            except OSError:
                raise BrokenPipeError("Socket connection broken")
            if chunk == b"":
                raise BrokenPipeError("Socket connection broken")
            self.recv_buffer += chunk
        end_char_loc = self.recv_buffer.index(end_char)
        msg = self.recv_buffer[:end_char_loc]
        self.recv_buffer = self.recv_buffer[end_char_loc + 1:]
        return msg.decode()

    def close(self):
        self.sock.close()
        logging.info("Socket closed")


def handle_socket_error(_func=None, cleanup=None):
    def decorator_handle_socket_error(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except BrokenPipeError:
                logging.error("Socket probably closed.")
                if cleanup is not None:
                    cleanup()
        return wrapper
    if _func is None:
        return decorator_handle_socket_error
    else:
        return decorator_handle_socket_error(_func)
