#!/usr/bin/env python3
"""
main.py
Project Mercury
Yovel Key-Cohen & Alwinfy
"""

from http_server.server import *
from http_server.log import *
from http_server.response import *
from account import *
import pickle
import time
import random



def create_navbar(active):
    """kwargs should be 'Home="home.html"'; active should be "home.html" """
    navbar = []
    pages = dict()
    cfg = open('conf/navbar.cfg', 'r')
    for line in list(reversed(cfg.read().split('\n'))):
        l = line.split(' ')
        pages[l[0]] = l[1]
    cfg.close()

    pitems = list(pages.keys())

    for i in pitems:
        navbar.append('<li><a href="{0}"{2}>{1}</a></li>'.format(pages[i], i, (' class="active-nav"' if pages[i] == active else '')))
    
    bar = '<center>\n\t<div id="menu-bar" class="menu-bar">\n\t\t<ul class="nav-bar">\n\t\t\t'\
     + '\n\t\t\t'.join(navbar)\
      + '\n\t\t\t<li class="page-title">Horothian Trade League</li>\n\t\t</ul>\n\t</div>\n</center>'

    return bar

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
    response = Response()

    if reqadr[0] == '':
        response.set_status_code(301, location='home.html')
        response.add_cookie('client-id', 'none')

    elif reqadr[0] == 'home.html':
        response.add_cookie('tester_restrictions', 'true')
        if cookies.get('client-id') != 'none':
            response.attach_file('home.html', rendr=True, navbar=create_navbar('home.html'))
        else:
            response.attach_file('account.html', rendr=True, navbar=create_navbar('home.html'))

    elif reqadr[0] == 'treaty.html':
        if cookies.get('tester_restrictions') == 'true':
            response.set_body(client_error_msg('Nothing here now.'))
        else:
            response.set_status_code(307, location='https://drive.google.com/open?id=1vylaFRMUhj0fCGqDVhn0RC7xXmOegabodKs9YK-8zbs')

    elif reqadr[0] == 'action':
        if not (len(req) > 2):
            self.send(Response.code(404))
            self.log.log('Client improperly requested an action.')
            return

        if reqadr[1] == 'pay':
            r = Response()
            sender_id = cookies.get('client-id')
            recipient_id = reqadr[2]
            amount = int(reqadr[3])
            recipient_acnt = list(filter(lambda u: u.id == recipient_id, accounts))[0]
            sender_acnt = list(filter(lambda u: u.id == sender_id, accounts))[0]

            if not sender_acnt.pay(amount, recipient_acnt):
                response.attach_file('pay_success.html')
                f = open('logs/transactions.log', 'a')
                f.write('{} -> {}; ${}'.format(sender_id, recipient_id, amount))
                f.close()
            else:
                response.attach_file('pay_failure.html')

        elif reqadr[1] == 'signup':
            username = reqadr[2]
            password = reqadr[3]
            id = '0000'
            while id != '1377' and id[0] != '00' and len(id) < 5:  # Saving first 100 accounts for admins
                id = '%04d' % random.randint(0, 10000)
            accounts.append(Account(username, password, id))
            response.add_cookie('client-id', id)
            response.attach_file('account.html')

        elif reqadr[1] == 'login':
            username = reqadr[2]
            password = reqadr[3]
            acnt = accounts.filter(lambda u: u.username == username and u.password == password)
            response.add_cookie('client-id', acnt.id)
            response.attach_file('account.html')

        elif reqadr[1] == 'shutdown':
            self.log.log('Initiating server shutdown...')
            if reqadr[2] == 'normal':
                self.close()
            elif reqadr[2] == 'force':
                exit()
            else:
                response.set_status_code(404)
        else:
            response.set_status_code(404)
            self.log.log('Client requested non-existent action.')
            return

    else:
        response.attach_file(reqadr[0], rendr=True, rendrtypes=('html', 'htm'), navbar=create_navbar(reqadr[0]))

    self.send(response)
    conn.close()


print(accounts)

s = Server(debug=True, include_debug_level=False)
s.set_request_handler(handle)
s.open()
save_users()
