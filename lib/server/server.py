"""
server.py
Project Mercury
Yovel Key-Cohen
"""

import socket
from lib.server.log import *
from lib.server.response import *

def get_error(num, let=''):
    codes = open('conf/errors.cfg', 'r').readlines()
    for line in codes:
        line = line.strip()
        if not (line == '' or line[0] == '#'):
            if int(line[:line.find(':')]) == num:
                return ('<center><div class="error">Error %d%s: ' % (num, let)) + line[line.find(':')+1:].strip()+'</div></center>'

class Server:
    def __init__(self, host=None, port=None, debug=False, include_debug_level=False):
        # Socket init stuff
        self.host = host if host else socket.gethostbyname(socket.gethostname())
        self.port = port if port else 8080
        self.buffer = 1024
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.running = True

        self.connection = None
        self.c_address = ['', 0]
        self.handled_counter = 0

        # On-board data management if needed
        self.state = {}
        self.data = {}
        self.debug = debug
        self.include_debug_level = include_debug_level
        self.log = Log(debug, include_debug_level)
        self.log.log("Server initialized successfully on", self.host + ':' + str(self.port), lvl=Log.STATUS)

    # Closes the server, ends program
    def close(self):
        self.socket.close()
        self.log.log("Server closed successfully.", lvl=Log.STATUS)
        self.log.dump()
        self.running = False
        print('Process exit.')

    # Sends a message; recommended to use Response class as a wrapper
    def send(self, msg):
        try:
            # You passed a string
            if type(msg) not in (type(bytes()), type(int())) and not isinstance(msg, Response):
                self.connection.send(Response(msg).compile())
            # You passed a Response
            elif isinstance(msg, Response):
                self.connection.send(msg.compile())
            # You passed a status code
            elif type(msg) == type(int()):
                self.connection.send(Response.code(msg))
            # You passed an already-encoded string
            else:
                self.connection.send(msg)
            #self.log.log("A response was sent to the client.")
        except AttributeError:
            self.log.log("Tried to send with no client connected.", lvl=Log.ERROR)
            return 1
        return 0

    # --(DEPRECATED)-- Easy way to send a file
    def send_file(self, faddr, custom_response=None):
        r = Response()
        if custom_response:
            r = custom_response
        r.attach_file(faddr)
        if '404' in r.header:
            self.log.log("Client requested non-existent file, returned 404.", lvl=Log.WARNING)
        self.send(r.compile())

    # Listens for a message, returns it decoded
    def recv(self):
        try:
            return self.connection.recv(self.buffer).decode(ENCODING)
        except AttributeError:
            self.log.log("Tried to receive with no client connected.", lvl=Log.ERROR)
            return 1
        except ConnectionResetError:
            self.log.log("Client forcibly closed existing connection.", lvl=Log.ERROR)
            return 1

    # Opens the server to requests
    def open(self):
        self.socket.listen(1)
        self.log.log("Server open, listening...", lvl=Log.STATUS)
        while self.running:
            try:
                self.connection, self.c_address = self.socket.accept()
            except (OSError, KeyboardInterrupt):  # When the server closed but tried to use socket
                break
            request = Request(self.recv())
            if request.req_list == 'ERROR_0':
                self.log.log('Client request is empty, ignoring.', lvl=Log.INFO)
                continue
            else:
                # Requests come in a list format, starting with 'GET' etc. and followed by the page address
                try:
                    self.handle_request(self, self.connection, self.c_address, request)
                except (KeyboardInterrupt, SystemExit):
                    self.close()
                except Exception as e:
                    if self.debug:
                        raise e
                    self.throwError(0, 'h', 'home.html')
                    self.log.log('A fatal error occurred in handle(): {}'.format(e), lvl=Log.ERROR)
            self.handled_counter += 1
            self.connection = None

    # Sends a user-friendly error message
    def throwError(self, code, id, page, response=None):
        err = get_error(code, id)
        if response is None:
            r = Response()
        else:
            r = response
        r.set_status_code(303, location=page)
        self.send(r)
        return err

    # Wrapper for request_handler() setting
    def set_request_handler(self, func):
        self.handle_request = func

    # Dummy, should be set in main.py; is called whenever a request is made
    def handle_request(self, IGNORE_THIS_PARAMETER, conn, addr, req):
        return 0


if __name__ == "__main__":
    s = Server()

    def handle(self, conn, addr, req):
        self.log.log("Client request:", req)
        if req[1] == '':
            self.send(Response.code(301, location='test.html'))
        else:
            self.send_file(req[1])
        # self.log.log("Client connection:", addr)
        conn.close()
        # self.log.log("Client connection closed")

    s.set_request_handler(handle)
    s.open()
