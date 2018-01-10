"""
main.py
Project Mercury
Yovel Key-Cohen
"""

from http_server.server import *
from http_server.log import *
from http_server.response import *
from account import *
import pickle
import time


def client_error_msg(msg):
    return '<html>' + msg + '<br><a href="home.html">Go back.</a></html>'

def load_users():
    userfile = open('data/users.dat', 'rb')
    try:
        users = pickle.load(userfile)
    except EOFError:
        users = [Account('Central Bank', 'password', '1377')]
    return users

def save_users():
    userfile = open('data/users.dat', 'wb')
    pickle.dump(accounts, userfile)

def parse_cookie(s):
    cookieA = s[8:].split(';')
    cookieB = dict()
    for term in cookieA:
        lt = list(term)
        try:
            sep = lt.index('=')
        except ValueError:
            return dict()
        cookieB[term[:sep].strip()] = term[sep + 1:].strip()
    return cookieB

accounts = load_users()


# ---------------------------------


def handle(self, conn, addr, req):
    self.log.log("Request from ", addr[0], ":", req)
    # Miles is not allowed to connect
    if addr[1] in ['10.1.3.179']:
        self.send("Your IP address has been banned temporarily.\
         For more information please visit haha you thought there would be more info but there's not bye loser.")
        self.log.log("Client IP was found banned -", addr[0])
        return

    cookies = parse_cookie(req[-1])

    if req[1] == '':
        self.send(Response.code301('home.html'))

    elif req[1] == 'home.html':
        r = Response()
        r.add_cookie('tester_restrictions', 'true')
        r.attach_file('home.html')
        self.send(r)

    elif req[1] == 'treaty.html':
        print(cookies)
        print(cookies.get('tester_restrictions'))
        if cookies.get('tester_restrictions') == 'true':
            self.send(Response(client_error_msg('Nothing here now.')))
        else:
            self.send(Response.code307('https://drive.google.com/open?id=1vylaFRMUhj0fCGqDVhn0RC7xXmOegabodKs9YK-8zbs'))

    else:
        r = Response()
        r.attach_file(req[1])
        self.send(r)

    conn.close()


print(accounts)

s = Server(True)
s.set_request_handler(handle)
s.open()
save_users()
