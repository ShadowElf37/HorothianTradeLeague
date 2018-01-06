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
        self.handled_counter = 0

        # On-board data management if needed
        self.state = {}
        self.data = {}

    def close(self):
        self.socket.close()

    def send(self, msg):
        try:
            if type(msg) != type(bytes()):
                self.connection.send(msg.encode(ENCODING))
            else:
                self.connection.send(msg)
        except AttributeError:
            print("Error: tried to send with no client connected")
            return 1
        return 0

    def send_file(self, faddr):
        ext1 = faddr[-3:]
        ext2 = faddr[-4:]
        ext3 = faddr[-5:]
        if ext2 in ('.png', '.jpg', '.gif', '.ico',) or ext3 in ('.jpeg',):
            faddr = self.get_image(faddr)
        elif ext2 in ('.htm',) or ext3 in ('.html',):
            faddr = self.get_page(faddr)
        elif ext2 in ('.css',) or ext1 in ('.js',):
            faddr = self.get_script_or_style(faddr)

        f = open(faddr, 'rb')
        self.send(f.read())
        f.close()

    @classmethod
    def get_image(cls, fname):
        return 'web/images/%s' % fname

    @classmethod
    def get_page(cls, fname):
        return 'web/%s' % fname

    @classmethod
    def get_script_or_style(cls, fname):
        return 'web/scripts_and_stylesheets/%s' % fname

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
            self.handle_request(self, self.connection, self.c_address, self.parse(self.recv()))
            self.handled_counter += 1

    def parse(self, request):
        request = request.split(' ')  # reduces GET xx HTTP to xx
        request = [request[0], request[1][1:]]
        request[1].split('/')
        return request

    def set_request_handler(self, func):
        self.handle_request = func

    def handle_request(self, IGNORE_THIS_PARAMETER, conn, addr, req):  # Should be set in main.py
        return 0

if __name__ == "__main__":
    s = Server()

    def handle(self, conn, addr, req):
        print(req)
        if req[1] == '':
            self.send_file("home.html")
        else:
            self.send_file(req[1])
        print("Connection!", addr)
        conn.close()

    s.set_request_handler(handle)
    print("Server open, listening...")
    s.open()