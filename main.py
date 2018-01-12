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
import random


def client_error_msg(msg):
    return '<html>' + msg + '<br><a href="home.html">Go back.</a></html>'

def load_users():
    userfile = open('data/users.dat', 'rb')
    try:
        users = pickle.load(userfile)
    except EOFError:
        print('user.dat empty, initializing with default values')
        users = [Account('CentralBank', 'password', '1377')]
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
    # A certain friend is not allowed to connect because he knows that sometimes I have webstuff
    # on my computer and might see this before it's ready for the grand opening
    if addr[0] in ['10.1.3.179']:
        self.send("Your IP address has been banned temporarily.\
         For more information please visit haha you thought there would be more info but there's not bye loser.")
        self.log.log("Client IP was found banned -", addr[0])
        return

    cookies = parse_cookie(req[-1])
    method = req[0]
    reqadr = req[1]

    if reqadr[0] == '':
        self.send(Response.code(301, location='home.html'))

    elif reqadr[0] == 'home.html':
        r = Response()
        r.add_cookie('tester_restrictions', 'true')
        r.attach_file('home.html')
        self.send(r)

    elif reqadr[0] == 'treaty.html':
        if cookies.get('tester_restrictions') == 'true':
            self.send(Response(client_error_msg('Nothing here now.')))
        else:
            self.send(Response.code(307, location='https://drive.google.com/open?id=1vylaFRMUhj0fCGqDVhn0RC7xXmOegabodKs9YK-8zbs'))

    elif reqadr[0] == 'action':
        if not (len(req) > 2):
            self.send(Response.code(404))
            self.log.log('Client improperly requested an action.')
            return

        if reqadr[1] == 'pay':
            sender_id = cookies.get('client-id')
            recipient_id = reqadr[2]
            amount = int(reqadr[3])
            recipient_acnt = list(filter(lambda u: u.id == recipient_id, accounts))[0]
            sender_acnt = list(filter(lambda u: u.id == sender_id, accounts))[0]

            if not sender_acnt.pay(amount, recipient_acnt):
                self.send_file('pay_success.html')
                f = open('logs/transactions.log', 'a')
                f.write('{} -> {}; ${}'.format(sender_id, recipient_id, amount))
                f.close()
            else:
                self.send_file('pay_failure.html')

        elif reqadr[1] == 'signup':
            username = reqadr[2]
            password = reqadr[3]
            id = '0000'
            while id != '1377' and id[0] != '00' and len(id) < 5:  # Saving first 100 accounts for admins
                id = '%04d' % random.randint(0, 10000)
            accounts.append(Account(username, password, id))
            response = Response()
            response.add_cookie('client-id', id)
            response.attach_file('account.html')
            self.send(response)

        elif reqadr[1] == 'login':
            username = reqadr[2]
            password = reqadr[3]
            acnt = accounts.filter(lambda u: u.username == username and u.password == password)
            response = Response()
            response.add_cookie('client-id', acnt.id)
            response.attach_file('account.html')
            self.send(response)

        elif reqadr[1] == 'shutdown':
            self.log.log('Initiating server shutdown...')
            if reqadr[2] == 'normal':
                self.close()
            elif reqadr[2] == 'force':
                exit()
            else:
                self.send(Response.code(404))
        else:
            self.send(Response.code(404))
            self.log.log('Client requested non-existent action.')
            return

    else:
        r = Response()
        r.attach_file(reqadr[0])
        self.send(r)

    conn.close()


print(accounts)

s = Server(debug=True, include_debug_level=False)
s.set_request_handler(handle)
s.open()
save_users()
