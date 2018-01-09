"""
response.py
Project Mercury
Yovel Key-Cohen
"""

ENCODING = 'UTF-8'


def get_image(fname):
    return 'web/images/%s' % fname

def get_page(fname):
    return 'web/%s' % fname

def get_script_or_style(fname):
    return 'web/scripts_and_stylesheets/%s' % fname


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

    @staticmethod
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
            faddr = get_image(faddr)
        elif ext2 in ('.htm',) or ext3 in ('.html',):
            faddr = get_page(faddr)
        elif ext2 in ('.css',) or ext1 in ('.js',):
            faddr = get_script_or_style(faddr)

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