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
        with open(dirname(realpath(__file__)) + '/codes.ini', 'r') as code:
            for line in code:
                self.codes[int(line.split()[0])] = ' '.join(line.split()[1:])

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
        ext = faddr.split('.')[-1].lower()
        if ext in ('png', 'jpg', 'jpeg', 'gif', 'ico'):
            faddr = 'web/assets/image/' + faddr
        elif ext in ('htm', 'html'):
            faddr = 'web/html/' + faddr
        elif ext in ('css'):
            faddr = 'web/css/' + faddr
        elif ext in ('js'):
            faddr = 'web/js/' + faddr
        elif ext in ('mp3'):
            faddr = 'web/assets/audio/' + faddr

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
