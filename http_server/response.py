"""
response.py
Project Mercury
Yovel Key-Cohen and Alwinfy
"""

ENCODING = 'UTF-8'

from os.path import dirname, realpath
from re import split


def create_navbar(active, logged_in):
    """kwargs should be 'Home="home.html"'; active should be "home.html" """
    navbar = []
    pages = []
    links = []
    cfg = open('conf/navbar.cfg', 'r')
    data = cfg.read()
    for line in list(reversed(data.split('\n'))):
        l = line.split(' ')
        l[0] = l[0].split('|')
        pages.append(l[0])
        links.append(l[1])
    cfg.close()

    for i in range(len(pages)):
        if (pages[i][0] != '_' and not logged_in) or (pages[i][1] != '_' and logged_in):
            navbar.append('<li><a href="{0}"{2}>{1}</a></li>'.format(links[i],
                                                                     (pages[i][0] if not logged_in else pages[i][-1]),
                                                                 (' class="active-nav"' if links[i] == active else '')))

    bar = '<center>\n\t<div id="menu-bar" class="menu-bar">\n\t\t<ul class="nav-bar">\n\t\t\t' \
          + '\n\t\t\t'.join(navbar) \
          + '\n\t\t\t<li class="page-title">Project Mercury</li>\n\t\t</ul>\n\t</div>\n</center>'

    return bar

def render(text, **resources):
    if type(text) == type(bytes()):
        text = text.decode(ENCODING)
    for i in list(resources.keys()):
        # print('#', '[['+i+']]')
        # print('@', resources[i])
        text = text.replace('[['+i+']]', str(resources[i]))
    return text.encode(ENCODING)


class Response:
    # Easy response codes
    REDIRECTS = [301, 302, 303, 307, 308]
    codes = {}
    ext = {}

    @staticmethod
    def code(hcode, **kwargs):
        r = Response(hcode)
        if hcode in Response.REDIRECTS:
            if kwargs.get("location") == None:
                raise TypeError("{} Errors must include redirect address".format(hcode))
            else:
                r.add_header_term('location', (kwargs["location"]))
        else:
            for k, v in kwargs:
                r.add_header_term(k, v)
        return r

    def __init__(self, code=200, body='', **kwargs):
        if len(self.codes) == 0:
            with open('conf/codes.cfg', 'r') as code:
                for line in code:
                    splitted = line.split()
                    Response.codes[int(splitted[0])] = ' '.join(splitted[1:])
            with open('conf/ext.cfg', 'r') as exts:
                for line in exts:
                    splitted = line.split()
                    for e in splitted[1:]:
                        Response.ext[e] = splitted[0]
        self.header = []
        self.header.append('HTTP/1.1 {} {}'.format(code, Response.codes.get(code, '[undefined]')))
        #print(self.header)
        self.cookie = []
        self.body = body
        self.logged_in = False

        if type(self.body) == type(int()):
            self.set_status_code(self.body, **kwargs)
            self.body = ''
        if len(self.codes) == 0:
            with open('conf/codes.cfg', 'r') as code:
                for line in code:
                    splitted = line.split()
                    Response.codes[int(splitted[0])] = ' '.join(splitted[1:])
            with open('conf/ext.cfg', 'r') as exts:
                for line in exts:
                    splitted = line.split()
                    for e in splitted[1:]:
                        Response.ext[e] = splitted[0]

    # Adds a field to the header (ie 'Set-Cookie: x=5')
    def add_header_term(self, field, string):
        #print(self.header)
        self.header.append("{}: {}".format('-'.join(i.title().replace("Id", "ID").replace("Md5", "MD5") for i in split('[ _-]+', field)), string))

    # Easier way of setting cookies than manually using add_header_term()
    def add_cookie(self, key, value, *flags):
        self.cookie.append(("Set-Cookie: %s=%s; " % (key, value)) + '; '.join(flags))

    # Sets the status code
    def set_status_code(self, code, **kwargs):
        self.header = Response.code(code, **kwargs).header

    # Sets the header; use if there's no other way
    def set_header(self, lst):
        self.header = lst

    # Sets body if you changed your mind after init
    def set_body(self, string):
        self.body = string

    # Puts a file in the body
    def attach_file(self, faddr, nb_page='none', logged_in=None, rendr=True, rendrtypes=(), error='', **renderopts):
        """faddr should be the file address accounting for ext.cfg
        rendr specifies whether the page should be rendered or not (so it doesn't try to render an image)
        rendrtypes adds extra control when you don't know if you'll be passed an image or a webpage and want to only render one; should be a tuple of files exts
        renderopts is what should be replaced with what; if you have [[value]], you will put value='12345' """

        if nb_page == 'none':
            nb_page = faddr
        renderopts['navbar'] = create_navbar(nb_page, self.logged_in if logged_in is None else logged_in)
        if type(rendrtypes) != type(tuple()):
            raise TypeError("rendrtypes requires tuple")
        suffix = self.ext.get(faddr.split('.')[-1], '')

        faddr = suffix + faddr
        # Actual body set
        try:
            f = open(faddr, 'rb')
            if rendr and (rendrtypes == () or faddr.split('.')[-1] in rendrtypes):
                fl = render(f.read(), error=error, **renderopts)
            else:
                fl = f.read()
            self.set_body(fl)
            f.close()

        except FileNotFoundError:
            self.set_status_code(404)

    # Throws together the header, cookies, and body, encoding them and adding whitespace
    def compile(self):
        return self.__bytes__()

    def __bytes__(self):
        try:
            b = self.body.encode(ENCODING)
        except AttributeError:
            b = self.body
        return '\r\n'.join(self.header).encode(ENCODING) + b'\r\n' + '\r\n'.join(self.cookie).encode(ENCODING) + b'\r\n' * (2 if self.cookie else 1) + b
