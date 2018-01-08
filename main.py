from server import *
from account import *
import pickle
from sys import exit


def load_users():
    userfile = open('users.dat', 'rb')
    try:
        users = pickle.load(userfile)
    except EOFError:
        users = [Account('1377')]
    return users

def save_users():
    userfile = open('users.dat', 'wb')
    pickle.dump(accounts, userfile)

accounts = load_users()

def parse_cookie(s):
    cookieA = s[8:].split(';')
    cookieB = dict()
    for term in cookieA:
        lt = list(term)
        try:
            sep = lt.index('=')
        except ValueError:
            return dict()
        cookieB[term[:sep]] = term[sep + 1:]
    return cookieB

def handle(self, conn, addr, req):
    self.log.log("Client request:", req)
    cookies = parse_cookie(req[2])

    if req[1] == '':
        self.send(Response.code301('home.html'))

    elif req[1] == 'home.html':
        r = Response()
        r.add_cookie('tester_restrictions', 'true')
        r.attach_file('home.html')
        self.send(r)

    elif req[1] == 'treaty.html':
        print(cookies.get('tester'))
        if cookies.get('tester_restrictions') == 'true':
            self.send(Response('Not right now.'))
        else:
            self.send(Response.code307('https://drive.google.com/open?id=1vylaFRMUhj0fCGqDVhn0RC7xXmOegabodKs9YK-8zbs'))

    else:
        r = Response()
        r.attach_file(req[1])
        self.send(r)

    print(cookies)
    conn.close()

print(accounts)

s = Server(True)
s.set_request_handler(handle)
s.open()
save_users()
