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
from encrypt import encrypt

def client_error_msg(msg):
    return '<html>' + msg + '<br><a href="home.html">Go back.</a></html>'


def load_users():
    userfile = open('data/users.dat', 'rb')
    try:
        users = pickle.load(userfile)
    except EOFError:
        print('user.dat empty, initializing with default values')
        users = [Account('Test', 'User', 'TestUser', 'password', '0001'), Account('League', 'Leader', 'LeagueLeader', 'password', '0002'), Account('Yovel', 'Key-Cohen', 'ShadowElf37', 'password', '0099'), Account('Central', 'Bank', 'CentralBank', 'password', '1377')]
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

def get_account_by_id(id):
    if id == 'none':
        return ShellAccount()
    try:
        a = list(filter(lambda u: u.id == id, accounts))[0]
    except IndexError:
        return ShellAccount()
    return a


accounts = load_users()

# ---------------------------------

def handle(self, conn, addr, req):
    self.log.log("Request from ", addr[0], ":", req)

    method = req[0]
    reqadr = req[1]
    cookies = parse_cookie(req[2])
    flags = req[3]

    response = Response()
    response.logged_in = cookies.get('client-id', 'none') != 'none'
    client_id = cookies.get('client-id')
    client = get_account_by_id(client_id)

    render_defaults = {'username':client.username, 'id':client_id, 'hunt_total':client.total_hunts, 'hunt_count':client.active_hunts, 'balance':client.balance}
    response.default_renderopts = render_defaults

    if client_id is None:
        response.add_cookie('client-id', 'none')
    elif response.logged_in:
        get_account_by_id(client_id).last_activity = time.strftime('%c - %x')
    if cookies.get('validator') != get_account_by_id(client_id).validator and response.logged_in:
        response.add_cookie('client-id', 'none')
        response.add_cookie('validator', 'none')
        response.set_status_code(307, location='account.html')
        response.logged_in = False
        self.send(response)
        conn.close()
        return


    get_last = lambda: cookies.get('page', 'home.html')

    if method == "GET":
        if reqadr[0] == '':
            response.set_status_code(307, location='home.html')
        elif reqadr[0] == 'home.html':
            if client_id == 'none':
                response.attach_file('home.html')
            else:
                response.attach_file('news.html', nb_page='home.html')

        elif reqadr[0] == 'treaty.html':
            if cookies.get('tester_restrictions') == 'true':
                response.set_body(client_error_msg('Nothing here now.'))
            else:
                response.set_status_code(307, location='https://drive.google.com/open?id=1vylaFRMUhj0fCGqDVhn0RC7xXmOegabodKs9YK-8zbs')

        elif reqadr[0] == 'account.html':
            account = get_account_by_id(client_id)
            if not account.shell:
                response.attach_file('account.html')
            else:
                response.attach_file('login.html', nb_page="account.html")

        elif reqadr[0] == 'pay.html':
            account = get_account_by_id(client_id)
            response.attach_file('pay.html', nb_page='account.html')

        elif reqadr[0] == 'signup.html':
            response.attach_file('signup.html', nb_page='account.html')

        elif reqadr[0] == 'transaction_history.html':
            cid = client_id
            acnt = get_account_by_id(cid)
            hist = []
            for item in acnt.transaction_history:
                item = item.split('|')
                hist.append('<tr>\n'+'<td>\n'+item[0]+'\n</td>'+'\n<td>'+item[1]+'\n</td>'+'\n<td>'+item[2]+'\n</td>''\n</tr>')
            response.attach_file('transaction_history.html', nb_page='account.html', history='\n'.join(hist))

        elif reqadr[0] == 'registry.html':
            acnts = []
            for a in sorted(accounts, key=lambda u: u.lastname if u.id not in ['0001', '0099', '1377'] else u.id):
                acnts.append('<tr>\n' + '<td>\n' + a.firstname + ' ' + a.lastname + '\n</td>' + '\n<td>' + a.id + '\n</td>' + '\n<td>' + a.coalition + '\n</td>' + '\n</tr>')
            response.attach_file('registry.html', nb_page='account.html', accounts='\n'.join(acnts))

        elif reqadr[0].split('.')[-1] == 'act':
            if reqadr[0] == 'logout.act':
                response.add_cookie('client-id', 'none')
                response.add_cookie('validator', 'none')
                response.attach_file('home.html', logged_in=False)
            elif reqadr[0] == 'shutdown_normal.act':
                self.log.log('Initiating server shutdown...')
                self.close()
                save_users()
                exit()
            elif reqadr[0] == 'shutdown_force.act':
                exit()
            else:
                # Proper error handling
                self.throwError(2, 'a', get_last(), response=response)
                self.log.log(addr[0], '- Client requested non-existent action.', lvl=Log.ERROR)


        else:
            # --THIS HANDLES EXTRANEOUS REQUESTS--
            # --PLEASE AVOID BY SPECIFYING MANUAL HANDLE CONDITIONS--
            # --INTENDED FOR IMAGES AND OTHER RESOURCES--
            response.attach_file(reqadr[0], rendr=True, rendrtypes=('html', 'htm'), nb_page=reqadr[0])

    elif method == "POST":
        # user=asd&pass=dsa --> {'user':'asd', 'pass':'dsa'}
        flags = {i.split('=')[0]:i.split('=')[1] for i in req[3][-1].split('&')}

        if reqadr[0] == 'login.act':
            usr = flags['user']
            pwd = flags['pass']
            try:
                acnt = list(filter(lambda u: u.username == usr and u.password == pwd, accounts))[0]

                response.add_cookie('client-id', acnt.id, 'Max-Age=604800', 'HttpOnly')
                response.add_cookie('validator', acnt.validator, 'Max-Age=604800', 'HttpOnly')

                response.set_status_code(303, location='account.html')
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
            while id == '1377' or id[:2] == '00' or get_account_by_id(id):  # Saving first 100 accounts for admin purposes
                id = '%04d' % random.randint(0, 9999)
                self.log.log("New account created with ID", id, "- first name is", first)
            acnt = Account(first, last, usr, pwd, id)
            accounts.append(acnt)

            response.add_cookie('client-id', id, 'Max-Age=604800', 'HttpOnly')
            response.add_cookie('validator', acnt.validator, 'Max-Age=604800', 'HttpOnly')

            response.set_status_code(303, location='account.html')

        elif reqadr[0] == 'pay.act':
            sender_id = client_id
            recipient_id = flags['recp']
            try:
                amount = int(flags['amt'])
            except ValueError:
                amount = float(flags['amt'])
            recipient_acnt = get_account_by_id(recipient_id)
            sender_acnt = get_account_by_id(sender_id)
            a = sender_acnt
            ar = recipient_acnt

            if not sender_acnt.pay(amount, recipient_acnt):
                response.attach_file('account.html')
                tid = '%19d' % random.randint(1, 2**64)
                f = open('logs/transactions.log', 'at')
                gl = '{0} -> {1}; Cr{2} ({3}) -- {4}\n'.format(sender_id, recipient_id, amount, tid, time.strftime('%c - %x'))
                f.write(gl)
                a.transaction_history.append('₢{} sent to {} {}|3{}|{}'.format(amount, ar.firstname, ar.lastname, tid, time.strftime('%c - %x')))
                if a.id != '1377':
                    ar.transaction_history.append('{} {} sent you ₢{}|2{}|{}'.format(a.firstname, a.lastname, amount, tid, time.strftime('%c - %x')))
                else:
                    ar.transaction_history.append('CB income of ₢{}|7{}|{}'.format(amount, tid, time.strftime('%c - %x')))
                f.close()
            else:
                response.attach_file('account.html') # error

    if reqadr[-1].split('.')[-1] == 'html':
        response.add_cookie('page', reqadr[-1])
    self.send(response)
    conn.close()


print(accounts)

s = Server(debug=True, include_debug_level=False)
s.set_request_handler(handle)
s.open()
save_users()
