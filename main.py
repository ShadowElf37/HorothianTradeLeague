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

def client_error_msg(msg):
    return '<html>' + msg + '<br><a href="home.html">Go back.</a></html>'


def load_users():
    userfile = open('data/users.dat', 'rb')
    try:
        users = pickle.load(userfile)
    except EOFError:
        print('user.dat empty, initializing with default values')
        users = [Account('Test', 'User', 'TestUser', 'password', '0001'), Account('Central', 'Bank', 'CentralBank', 'password', '1377')]
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
def get_account_by_id(id):
    if id == 'none':
        return None
    a = list(filter(lambda u: u.id == id, accounts))[0]
    return a

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

    method = req[0]
    reqadr = req[1]
    cookies = parse_cookie(req[2])
    flags = req

    response = Response()
    if method == "GET":
        if reqadr[0] == '':
            response.set_status_code(307, location='home.html')
            if cookies.get('client-id') is None:
                response.add_cookie('client-id', 'none')

        elif reqadr[0] == 'home.html':
            response.add_cookie('tester_restrictions', 'true')
            if cookies.get('client-id') == 'none':
                response.attach_file('home.html')
            else:
                response.attach_file('news.html', nb_page='home.html')

        elif reqadr[0] == 'treaty.html':
            if cookies.get('tester_restrictions') == 'true':
                response.set_body(client_error_msg('Nothing here now.'))
            else:
                response.set_status_code(307, location='https://drive.google.com/open?id=1vylaFRMUhj0fCGqDVhn0RC7xXmOegabodKs9YK-8zbs')

        elif reqadr[0] == 'account.html':
            account = get_account_by_id(cookies.get('client-id'))
            response.attach_file('account.html', username=account.username, id=account.id, balance=account.balance)

        elif reqadr[0] == 'pay.html':
            account = get_account_by_id(cookies.get('client-id'))
            response.attach_file('pay.html', balance=account.balance)

        elif reqadr[0].split('-')[0] == 'action':
            reqadr = reqadr[0].split('-')
            if not (len(req) > 2):
                self.send(Response.code(404))
                self.log.log('Client improperly requested an action.')
                return

            if reqadr[1] == 'pay.act':
                sender_id = cookies.get('client-id')
                recipient_id = reqadr[2]
                amount = int(reqadr[3])
                recipient_acnt = get_account_by_id(recipient_id)
                sender_acnt = get_account_by_id(sender_id)

                if not sender_acnt.pay(amount, recipient_acnt):
                    response.attach_file('pay_success.html')
                    f = open('logs/transactions.log', 'a')
                    f.write('{} -> {}; ${}'.format(sender_id, recipient_id, amount))
                    f.close()
                else:
                    response.attach_file('pay_failure.html')

            elif reqadr[1] == 'signup.act':
                username = reqadr[2]
                password = reqadr[3]
                id = '0000'
                while id != '1377' and id[0] != '00' and len(id) < 5:  # Saving first 100 accounts for admins
                    id = '%04d' % random.randint(0, 10000)
                accounts.append(Account(username, password, id))
                response.add_cookie('client-id', id)
                response.attach_file('account.html')

            elif reqadr[1] == 'login.act':
                username = reqadr[2]
                password = reqadr[3]
                try:
                    acnt = list(filter(lambda u: u.username == username and u.password == password, accounts))[0]
                    response.add_cookie('client-id', acnt.id)
                    account = get_account_by_id(cookies.get('client-id'))
                    response.attach_file('account.html', nb_page='home.html', username=account.username, id=account.id, balance=account.balance)
                except IndexError:
                    response.attach_file('home.html')  # an incorrect username or password, should be changed

            elif reqadr[1] == 'logout.act':
                response.add_cookie('client-id', 'none')
                response.attach_file('home.html')

            elif reqadr[1] == 'shutdown.act':
                self.log.log('Initiating server shutdown...')
                if reqadr[2] == 'normal':
                    self.close()
                    exit()
                elif reqadr[2] == 'force':
                    exit()
                else:
                    response.set_status_code(404)
            else:
                response.set_status_code(404)
                self.log.log('Client requested non-existent action.')
                return

        else:
            response.attach_file(reqadr[0], rendr=True, rendrtypes=('html', 'htm'), nb_page=reqadr[0])

    elif method == "POST":
        # user=asd&pass=dsa --> {'user':'asd', 'pass':'dsa'}
        flags = {i.split('=')[0]:i.split('=')[1] for i in req[3][-1].split('&')}

        if reqadr[0] == 'login.act':
            usr = flags['user']
            pwd = flags['pass']
            try:
                acnt = list(filter(lambda u: u.username == usr and u.password == pwd, accounts))[0]
                response.add_cookie('client-id', acnt.id)
                #account = get_account_by_id(cookies.get('client-id'))
                response.attach_file('account.html', nb_page='home.html', username=acnt.username, id=acnt.id,
                                     balance=acnt.balance)
            except IndexError:
                response.attach_file('home.html')  # an incorrect username or password, should be changed

        elif reqadr[0] == 'signup.act':
            first = flags['first']
            last = flags['last']
            usr = flags['user']
            pwd = flags['pass']
            cpwd = flags['cpass']  # confirm password
            if cpwd != pwd:
                raise ValueError('Please implement an error page thanks :XXDX::D:X')
            id = '0000'
            while id == '1377' or id[:2] == '00':  # Saving first 100 accounts for admin purposes
                id = '%04d' % random.randint(0, 9999)
                self.log.log("New account created with ID", id, "- first name is", first)
            a = Account(first, last, usr, pwd, id)
            accounts.append(a)
            response.add_cookie('client-id', id)
            response.attach_file('account.html', username=a.username, id=a.id, balance=a.balance)

        elif reqadr[0] == 'pay.act':
            sender_id = cookies.get('client-id')
            recipient_id = flags['recp']
            try:
                amount = int(flags['amt'])
            except ValueError:
                amount = float(flags['amt'])
            recipient_acnt = get_account_by_id(recipient_id)
            sender_acnt = get_account_by_id(sender_id)
            a = sender_acnt

            if not sender_acnt.pay(amount, recipient_acnt):
                response.attach_file('account.html', username=a.username, id=a.id, balance=a.balance)
                f = open('logs/transactions.log', 'a')
                f.write('{} -> {}; ${}'.format(sender_id, recipient_id, amount))
                f.close()
            else:
                response.attach_file('account.html', username=a.username, id=a.id, balance=a.balance)

    self.send(response)
    conn.close()


print(accounts)

s = Server(debug=True, include_debug_level=False)
s.set_request_handler(handle)
s.open()
save_users()
