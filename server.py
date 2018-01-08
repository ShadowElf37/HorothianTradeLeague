"""
server.py
Project Mercury
Yovel Key-Cohen
"""

import socket
import time
from sys import exit

ENCODING = 'UTF-8'


class Log:
    STATUS = 'STATUS'
    INFO = 'INFO'
    WARNING = 'WARNING'
    ERROR = 'ERROR'

    """For tracking information; use over print for the automatic timestamps."""
    def __init__(self, debug=False, include_level=False):
        self.ledger = []
        self.debug = debug
        self.include_level = include_level

    # Logs any number of strings in its ledger
    def log(self, *event, lvl=INFO):
        event = tuple(map(str, event))
        if self.include_level:
            item = (lvl, self.get_time(), ' '.join(event))
        else:
            item = (self.get_time(), ' '.join(event))
        if self.debug:
            print(item)
        self.ledger.append(item)

    # Dumps the current ledger to a unique log file; should be called on server close
    def dump(self):
        # Gets current log number
        lcf = open("logs/log_counter.dat", 'w+')
        lc = int(lcf.read())
        lcf.write(str(lc+1))
        lcf.close()

        # Creates file and writes ledger
        f = open("logs/%d_log%s.log" % (lc, Log.get_time_alt()), 'w')
        f.write('\n'.join(self.ledger))
        f.close()

    # Gets a timestamp
    @staticmethod
    def get_time():
        timestamp = time.strftime('%d %H:%M:%S')
        return timestamp

    # Gets a timestamp (made for dump())
    @staticmethod
    def get_time_alt():
        timestamp = time.strftime('%y-%m-%d-%H-%M-%S')
        return timestamp


class Response:
    # Easy response codes
    @staticmethod
    def code404(*args):
        """Not found"""
        r = Response()
        r.set_header('HTTP/1.1 404 Not Found')
        return r

    @staticmethod
    def code451(*args):
        """Unavailable for legal reasons"""
        r = Response()
        r.set_header('HTTP/1.1 451 Unavailable For Legal Reasons')
        return r

    @staticmethod
    def code301(*args):
        """Permanently moved"""
        r = Response()
        if len(args) < 1:
            raise TypeError("301 Errors must include redirect address")
        r.set_header('HTTP/1.1 301 Moved Permanently')
        r.add_header_term('Location: %s' % args[0])
        return r

    def code307(*args):
        """Temporarily moved"""
        r = Response()
        if len(args) < 1:
            raise TypeError("307 Errors must include redirect address")
        r.set_header('HTTP/1.1 307 Temporary Redirect')
        r.add_header_term('Location: %s' % args[0])
        return r

    @staticmethod
    def code200():
        """Success"""
        r = Response()
        r.set_header('HTTP/1.1 200 OK')
        return r

    @staticmethod
    def code204():
        """Not returning any body"""
        r = Response()
        r.set_header('HTTP/1.1 204 No Content')
        return r

    def __init__(self, body=''):
        self.header = ['HTTP/1.1 200 OK']
        self.cookie = []
        self.body = body

    # Adds a field to the header (ie 'Set-Cookie: x=5')
    def add_header_term(self, string):
        self.header.append('%s' % string)

    # Easier way of setting cookies than manually using add_header_term()
    def add_cookie(self, key, value, *flags):
        self.cookie.append(("Set-Cookie: %s=%s; " % (key, value)) + '; '.join(flags))

    # Sets the status code; should only be used if no preset is available
    def set_status_code(self, code):
        self.header[0] = 'HTTP/1.1 %s' % code

    # Sets the header; use if there's no other way
    def set_header(self, string):
        self.header[0] = string

    # Sets body if you changed your mind after init
    def set_body(self, string):
        self.body = string

    # Puts a file in the body if you don't want to use Server's send_file()
    def attach_file(self, faddr):
        ext1 = faddr[-3:]
        ext2 = faddr[-4:]
        ext3 = faddr[-5:]
        if ext2 in ('.png', '.jpg', '.gif', '.ico',) or ext3 in ('.jpeg',):
            faddr = Server.get_image(faddr)
        elif ext2 in ('.htm',) or ext3 in ('.html',):
            faddr = Server.get_page(faddr)
        elif ext2 in ('.css',) or ext1 in ('.js',):
            faddr = Server.get_script_or_style(faddr)

        # Actual send
        try:
            f = open(faddr, 'rb')
            self.set_body(f.read())
            f.close()
        except FileNotFoundError:
            self.set_header('HTTP/1.1 404 Not Found')

    # Throws together the header, cookies, and body, encoding them and adding whitespace
    def compile(self):
        return self.__bytes__()

    def __bytes__(self):
        try:
            b = self.body.encode(ENCODING)
        except AttributeError:
            b = self.body
        return '\r\n'.join(self.header).encode(ENCODING) + b'\r\n' + '\r\n'.join(self.cookie).encode(ENCODING) + b'\r\n' * (2 if self.cookie else 1) + b


class Server:
    def __init__(self, debug=False, include_debug_level=False):
        # Socket init stuff
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
        self.log = Log(debug, include_debug_level)
        self.log.log("Server initialized successfully.", lvl=Log.STATUS)

    # Closes the server, ends program
    def close(self):
        self.socket.close()
        self.log.log(Log.STATUS, "Server closed successfully.", lvl=Log.STATUS)
        self.log.dump()
        exit()

    # Sends a message; recommended to use Response class as a wrapper
    def send(self, msg):
        try:
            if type(msg) != type(bytes()) and not isinstance(msg, Response):
                self.connection.send(Response(msg).compile())
            elif isinstance(msg, Response):
                self.connection.send(msg.compile())
            else:
                self.connection.send(msg)
        except AttributeError:
            self.log.log("Tried to send with no client connected.", lvl=Log.ERROR)
            return 1
        return 0

    # Easy way to send a file
    def send_file(self, faddr, custom_response=None):
        # Automatically assume folder for certain file types; should only supply file name in parameters
        ext1 = faddr[-3:]
        ext2 = faddr[-4:]
        ext3 = faddr[-5:]
        if ext2 in ('.png', '.jpg', '.gif', '.ico',) or ext3 in ('.jpeg',):
            faddr = self.get_image(faddr)
        elif ext2 in ('.htm',) or ext3 in ('.html',):
            faddr = self.get_page(faddr)
        elif ext2 in ('.css',) or ext1 in ('.js',):
            faddr = self.get_script_or_style(faddr)

        # Actual send
        try:
            f = open(faddr, 'rb')
            if custom_response:
                custom_response.set_body(f.read())
                r = custom_response
            else:
                r = Response(f.read())
            self.send(r.compile())
            f.close()
        except (FileNotFoundError, OSError):
            self.log.log("Client requested non-existent file, returned 404.", lvl=Log.WARNING)
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

    # Listens for a message, returns it decoded
    def recv(self):
        try:
            return self.connection.recv(self.buffer).decode(ENCODING)
        except AttributeError:
            self.log.log("Tried to receive with no client connected.", lvl=Log.ERROR)
            return 1

    # Opens the server to requests
    def open(self):
        self.socket.listen(1)
        self.log.log("Server open, listening...", lvl=Log.STATUS)
        while True:
            self.connection, self.c_address = self.socket.accept()
            parsed_req = self.parse(self.recv())
            if parsed_req == 'ERROR_0':
                self.log.log('Client request is empty, ignoring.', lvl=Log.INFO)
                continue
            else:
                # Requests come in a list format, starting with 'GET' etc. and followed by the page address
                self.handle_request(self, self.connection, self.c_address, parsed_req)
            self.handled_counter += 1
            self.connection = None

    # Parses the request, simplies to important information
    def parse(self, request):
        # Get the cookies
        p = request
        cookie = ''
        for field in p.split('\n'):
            if 'Cookie' in field:
                cookie = field.strip()
        # Reduce the request to a list
        request = request.split(' ')
        try:
            request = [request[0], request[1][1:], cookie]  # [GET, xx, 'Cookie: a=b']
        except IndexError:  # Sometimes this happens?
            return 'ERROR_0'
        request[1].split('/')
        return request

    # Wrapper for request_handler() setting
    def set_request_handler(self, func):
        self.handle_request = func

    # Dummy, should be set in main.py; is called whenever a request is made
    def handle_request(self, IGNORE_THIS_PARAMETER, conn, addr, req):
        return 0

"""
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
"""