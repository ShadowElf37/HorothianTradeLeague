"""
response.py
Project Mercury
Yovel Key-Cohen
"""

ENCODING = 'UTF-8'

from os.path import dirname, realpath

class Response:
    # Easy response codes
    REDIRECTS = [301, 307]
    @staticmethod
    def code(hcode, **kwargs):
        r = Response()
        r.set_header('HTTP/1.1 {} {}'.format(hcode, r.codes[hcode]))
        if hcode in Response.REDIRECTS:
            if kwargs.get("location") == None:
                raise TypeError("{} Errors must include redirect address".format(hcode))
            else:
                r.add_header_term("Location: {}".format(kwargs["location"]))
        return r

    def __init__(self, body=''):
        self.header = ['HTTP/1.1 200 OK']
        self.cookie = []
        self.body = body
        self.codes = dict()
        self.ext = dict()
        with open('conf/codes.cfg', 'r') as code:
            for line in code:
                splitted = line.split()
                self.codes[int(splitted[0])] = ' '.join(splitted[1:])
        with open('conf/ext.cfg', 'r') as exts:
            for line in exts:
                splitted = line.split()
                for e in splitted[1:]:
                    self.ext[e] = splitted[0]

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
        prefix = self.ext.get(faddr.split('.')[-1], None)
        if not prefix:
            raise TypeError("Extension unknown.")
        faddr = prefix + faddr
        # Actual body set
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
