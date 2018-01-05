import socket
import pickle
from sys import exit

ENCODING = 'UTF-8'

class Response:
    def __init__(self, body):
        self.header = ['HTTP/1.1 200 OK\n']
        self.cookie = []
        self.body = body

    def add_header_term(self, string):
        self.header.append('\n%s' % string.encode(ENCODING))

    def add_cookie(self, key, value, *flags):
        self.cookie.append(("Set-Cookie: %s=%s; " % (key, value)) + '; '.join(flags))

    def get_response(self):
        return '\n'.join(self.header).encode(ENCODING) + '\n' + '\n'.join(self.cookie).encode(ENCODING)

class Server:
    def __init__(self):
        self.host = socket.gethostbyname(socket.gethostname())
        self.port = 80
        self.buffer = 1024
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))

        self.connection = None
        self.c_address = ['', 0]

        # On-board data management if needed
        self.state = {}
        self.data = {}

    def close(self):
        self.socket.close()

    def send(self, msg):
        try:
            self.connection.send(msg.encode(ENCODING))
        except AttributeError:
            print("Error: tried to send with no client connected")
            return 1
        return 0

    def recv(self):
        try:
            return self.connection.recv(self.buffer).decode(ENCODING)
        except AttributeError:
            print("Error: tried to receive with no client connected")
            return 1

    def open(self):
        self.socket.listen(1)
        while True:
            self.connection, self.c_address = self.socket.accept()
            self.handle_request(self.connection, self.c_address, self.parse(self.recv()))

    def parse(self, request):
        request = request.split(' ')[1][1:]  # reduces GET xx HTTP to xx
        request.split('/')
        request.remove('')
        return request

    def handle_request(self, conn, addr, req):  # Should be set in main.py
        return 0
