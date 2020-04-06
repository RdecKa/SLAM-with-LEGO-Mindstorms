import logging
import socket


class Socket():
    def __init__(self, host, port):
        logging.info(f"Establishing a socket to {host}:{port}")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.recv_buffer = b""
        logging.info(f"Socket to {host}:{port} established")

    def send(self, message: str, end_char=b"\0"):
        total = 0
        msg = message.encode() + end_char
        while total < len(msg):
            sent = self.sock.send(msg[total:])
            if sent == 0:
                raise RuntimeError("Socket connection broken")
            total += sent

    def receive(self, end_char=b"\0"):
        while end_char not in self.recv_buffer:
            chunk = self.sock.recv(1024)
            if chunk == b"":
                raise RuntimeError("Socket connection broken")
            self.recv_buffer += chunk
        end_char_loc = self.recv_buffer.index(end_char)
        msg = self.recv_buffer[:end_char_loc]
        self.recv_buffer = self.recv_buffer[end_char_loc + 1:]
        return msg.decode()

    def close(self):
        self.sock.close()
        logging.info("Socket closed")
