import socket
import pickle
import time
from sys import exit

ENCODING = 'UTF-8'

class Log:
    def __init__(self, debug=False):
        self.ledger = []
        self.debug = debug

    def log(self, *event):
        event = tuple(map(str, event))
        item = (self.get_time(), ' '.join(event))
        if self.debug:
            print(item)
        self.ledger.append(item)

    @staticmethod
    def get_time():
        timestamp = time.strftime('%y/%m/%d %H:%M:%S')
        return timestamp


class Response:
    @staticmethod
    def code404(*args):
        """Not found"""
        return 'HTTP/1.1 404 Not Found'

    @staticmethod
    def code301(*args):
        """Permanently moved"""
        if len(args) < 1:
            raise TypeError("301 Error must include redirect address")
        return 'HTTP/1.1 301 Moved Permanently\r\nLocation: /%s' % args[0]

    @staticmethod
    def code200():
        """Success"""
        return 'HTTP/1.1 200 OK'

    @staticmethod
    def code204():
        """Not returning any body"""
        return 'HTTP/1.1 204 No Content'

    def __init__(self, body):
        self.header = ['HTTP/1.1 200 OK']
        self.cookie = []
        self.body = body

    def add_header_term(self, string):
        self.header.append('%s' % string)

    def add_cookie(self, key, value, *flags):
        self.cookie.append(("Set-Cookie: %s=%s; " % (key, value)) + '; '.join(flags))

    def set_status_code(self, integer):
        self.header[0] = 'HTTP/1.1 %d OK'

    def compile(self):
        return self.__bytes__()

    def __bytes__(self):
        try:
            return '\r\n'.join(self.header).encode(ENCODING) + b'\r\n' + '\r\n'.join(self.cookie).encode(ENCODING) + b'\r\n' + self.body.encode(ENCODING)
        except AttributeError:
            return '\r\n'.join(self.header).encode(ENCODING) + b'\r\n' + '\r\n'.join(self.cookie).encode(ENCODING) + b'\r\n' + self.body


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
        self.log = Log(True)
        self.log.log("Server initialized successfully.")

    def close(self):
        self.socket.close()
        self.log.log("Server closed successfully.")

    def send(self, msg):
        try:
            if type(msg) != type(bytes()):
                self.connection.send(msg.encode(ENCODING))
            elif isinstance(msg, Response):
                self.connection.send(bytes(msg))
            else:
                self.connection.send(msg)
        except AttributeError:
            self.log.log("Error: tried to send with no client connected.")
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

        try:
            f = open(faddr, 'rb')
            self.send(Response(f.read()).compile())
            f.close()
        except FileNotFoundError:
            self.log.log("Client requested non-existent file, returned 404.")
            self.send(Response.code404())

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
            self.log.log("Error: tried to receive with no client connected.")
            return 1

    def open(self):
        self.socket.listen(1)
        self.log.log("Server open, listening...")
        while True:
            self.connection, self.c_address = self.socket.accept()
            parsed_req = self.parse(self.recv())
            if parsed_req == 'ERROR_0':
                self.log.log('Client request is empty, ignoring.')
                continue
            else:
                self.handle_request(self, self.connection, self.c_address, parsed_req)
            self.handled_counter += 1

    def parse(self, request):
        request = request.split(' ')
        try:
            request = [request[0], request[1][1:]]# reduces GET xx HTTP to xx
        except IndexError:
            return 'ERROR_0'
        request[1].split('/')
        return request

    def set_request_handler(self, func):
        self.handle_request = func

    def handle_request(self, IGNORE_THIS_PARAMETER, conn, addr, req):  # Should be set in main.py
        return 0

if __name__ == "__main__":
    s = Server()

    def handle(self, conn, addr, req):
        self.log.log("Client request:", req)
        if req[1] == '':
            self.send(Response.code301('test.html'))
        else:
            self.send_file(req[1])
        # self.log.log("Client connection:", addr)
        conn.close()
        # self.log.log("Client connection closed")

    s.set_request_handler(handle)
    s.open()