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


ids_to_hundred = list(map(lambda i: '%04d' % i, range(0, 100)))
admin_accounts = tuple(ids_to_hundred + ['1377',])
del ids_to_hundred

def load_users():
    userfile = open('data/users.dat', 'rb')
    try:
        users = pickle.load(userfile)
    except EOFError:
        print('user.dat empty, initializing with default values')
        users = [
                    Account('Test', 'User', 'TestUser', 'password', '', admin_accounts[0]),
                    # Account('League', 'Leader', 'LeagueLeader', 'password', '', admin_accounts[1]),
                    Account('Yovel', 'Key-Cohen', 'ShadowElf37', 'password', 'yovelkeycohen@gmail.com', admin_accounts[99]),
                    Account('Central', 'Bank', 'CentralBank', 'password', 'ykey-cohen@emeryweiner.org', admin_accounts[100])
                 ]
        for a in users:
            a.admin = True
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
def get_account_by_name(firstname, lastname):
    try:
        a = list(filter(lambda u: u.firstname == firstname and u.lastname == lastname, accounts))[0]
    except IndexError:
        return ShellAccount()
    return a
def get_account_by_username(username):
    try:
        a = list(filter(lambda u: u.username == username, accounts))[0]
    except IndexError:
        return ShellAccount()
    return a
def get_account_by_email(email):
    try:
        a = list(filter(lambda u: u.email == email, accounts))[0]
    except IndexError:
        return ShellAccount()
    return a

def td_wrap(s):
    return '\n<td>' + s + '</td>'

whitelist = open('conf/whitelist.cfg', 'r').readlines()
accounts = load_users()
error = ''

# ---------------------------------

def handle(self, conn, addr, req):
    global error
    self.log.log("Request from ", addr[0], ":", req)

    method = req[0]
    reqadr = req[1]
    cookies = parse_cookie(req[2])
    flags = req[3]

    response = Response()
    response.logged_in = cookies.get('client-id', 'none') != 'none'
    client_id = cookies.get('client-id')
    client = get_account_by_id(client_id)

    # Legacy solution to the error-handling fiasco, no longer needed
    #hist = ['<tr>\n' + '<td>\n' + item.split('|')[0] + '\n</td>' + '\n<td>' + item.split('|')[1] + '\n</td>' + '\n<td>' + item.split('|')[
            #2] + '\n</td>''\n</tr>' for item in client.transaction_history]
    #ac = ['<tr>\n' + '<td>\n' + a.firstname + ' ' + a.lastname + '\n</td>' + '\n<td>' + a.id + '\n</td>' + '\n<td>' + a.coalition + '\n</td>' + '\n</tr>'\
            #for a in sorted(accounts, key=lambda u: u.lastname if u.id not in admin_accounts else u.id)]

    render_defaults = {'error':error, 'username':client.username, 'id':client_id, 'hunt_total':client.total_hunts, 'hunt_count':client.active_hunts, 'balance':client.balance}
    response.default_renderopts = render_defaults

    if client_id is None:
        response.add_cookie('client-id', 'none')
    elif cookies.get('validator') != get_account_by_id(client_id).validator and response.logged_in:
        response.add_cookie('client-id', 'none')
        response.add_cookie('validator', 'none')
        response.logged_in = False
        error = self.throwError(5, 'a', '/login.html', response=response)
        self.log.log(addr[0], '- Client\'s cookies don\'t match.', lvl=Log.ERROR)
        return
    elif response.logged_in:
        get_account_by_id(client_id).last_activity = time.strftime('%X (%x)')


    get_last = lambda: cookies.get('page', 'home.html')

    if method == "GET":
        if reqadr[0] == '':
            response.set_status_code(307, location='/home.html')
        elif reqadr[0] == 'home.html':
            if client_id == 'none':
                response.attach_file('home.html')
            else:
                response.set_status_code(307, location='/news.html')

        elif reqadr[0] == 'news.html':
            response.attach_file('news.html', nb_page='home.html')

        elif reqadr[0] == 'treaty.html':
            response.set_body(client_error_msg('Nothing here now.'))
            # response.set_status_code(307, location='https://drive.google.com/open?id=1vylaFRMUhj0fCGqDVhn0RC7xXmOegabodKs9YK-8zbs')

        elif reqadr[0] == 'account.html':
            account = get_account_by_id(client_id)
            if not account.shell:
                response.attach_file('account.html')
            else:
                response.set_status_code(307, location='/login.html')

        elif reqadr[0] == 'login.html':
            response.attach_file('login.html', nb_page="account.html")

        elif reqadr[0] == 'pay.html':
            response.attach_file('pay.html', nb_page='account.html')

        elif reqadr[0] == 'signup.html':
            response.attach_file('signup.html', nb_page='account.html')

        elif reqadr[0] == 'transaction_history.html':
            cid = client_id
            acnt = get_account_by_id(cid)
            hist = []
            for item in acnt.transaction_history:
                item = item.split('|')
                hist.append('<tr>'+td_wrap(item[0])+td_wrap(item[1])+td_wrap(item[2])+'\n</tr>')
            response.attach_file('transaction_history.html', nb_page='account.html', history='\n'.join(hist))

        elif reqadr[0] == 'registry.html':
            acnts = []
            for a in sorted(accounts, key=lambda u: u.lastname if not u.admin else u.id):
                acnts.append('<tr>' + td_wrap(a.firstname + ' ' + a.lastname) + td_wrap(a.id) + td_wrap(a.coalition) + td_wrap(a.last_activity) + td_wrap(a.date_of_creation) + '\n</tr>')
            response.attach_file('registry.html', nb_page='account.html', accounts='\n'.join(acnts))

        elif reqadr[0] == 'messages.html':
            messages = []
            for msg in sorted(client.messages, key=lambda m: -float(m.sort_date)):
                m = '<div class="preview">\n\t<span class="sender">{}</span><br>\n\t<span class="subject">{}</span>\n\t<span class="date">{}</span>\n</div>'.format(
                    msg.sender.get_name(),
                    msg.subject,
                    msg.formal_date
                    )
                messages.append(m)
            response.attach_file('messages.html', nb_page='account.html', messages='\n'.join(messages))

        # ACTIONS
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
                error = self.throwError(2, 'a', get_last(), response=response)
                self.log.log(addr[0], '- Client requested non-existent action.', lvl=Log.ERROR)
                return

        # MESSAGE FILES
        elif reqadr[0] == 'm':
            print('m')
            try:
                d = open('data/messages/' + reqadr[1] + '.msg', 'r').read()
                response.body = d
            except FileNotFoundError:
                response.body = "|ERR|"
                self.log.log(addr[0], '- Client requested non-existent message file.', lvl=Log.ERROR)


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

            if not all(flags.values()):
                error = self.throwError(13, 'a', get_last(), response=response)
                self.log.log(addr[0], '- Client POSTed empty values.', lvl=Log.ERROR)
                return
            elif get_account_by_username(usr).blacklisted:
                error = self.throwError(14, 'a', get_last(), response=response)
                self.log.log(addr[0], '- Client tried to log in to banned account.', lvl=Log.ERROR)
                return

            try:
                acnt = list(filter(lambda u: u.username == usr and u.password == pwd, accounts))[0]

                response.add_cookie('client-id', acnt.id, 'Max-Age=604800', 'HttpOnly')  # 2 weeks
                response.add_cookie('validator', acnt.validator, 'Max-Age=604800', 'HttpOnly')

                response.set_status_code(303, location='account.html')
            except IndexError:
                error = self.throwError(4, 'a', get_last(), response=response)
                self.log.log(addr[0], '- Client entered incorrect login information.', lvl=Log.ERROR)
                return

        elif reqadr[0] == 'signup.act':
            first = flags['first']
            last = flags['last']
            mail = flags['mail']
            usr = flags['user']
            pwd = flags['pass']
            cpwd = flags['cpass']  # confirm password

            if not all(flags.values()):
                error = self.throwError(13, 'b', get_last(), response=response)
                self.log.log(addr[0], '- Client POSTed empty values.', lvl=Log.ERROR)
                return

            elif not get_account_by_name(first, last).shell:
                error = self.throwError(8, 'a', get_last(), response=response)
                self.log.log(addr[0], '- Client tried to sign up with already-used name.', lvl=Log.ERROR)
                return

            elif not get_account_by_username(usr).shell:
                error = self.throwError(9, 'a', get_last(), response=response)
                self.log.log(addr[0], '- Client tried to sign up with already-used username.', lvl=Log.ERROR)
                return

            elif not first+' '+last in whitelist:
                error = self.throwError(10, 'a', get_last(), response=response)
                self.log.log(addr[0], '- Forbidden signup attempt.', lvl=Log.ERROR)
                return

            elif not get_account_by_email(mail):
                error = self.throwError(12, 'a', get_last(), response=response)
                self.log.log(addr[0], '- Client tried to sign up with already-used email.', lvl=Log.ERROR)
                return

            elif cpwd != pwd:
                error = self.throwError(7, 'a', get_last(), response=response)
                self.log.log(addr[0], '- Client pwd does not equal confirm pwd.', lvl=Log.ERROR)
                return

            id = '0000'
            while id in ('1377',) or id[:2] == '00' or not get_account_by_id(id).shell:  # Saving first 100 accounts for admin purposes
                id = '%04d' % random.randint(0, 9999)
                self.log.log("New account created with ID", id, "- first name is", first)
            acnt = Account(first, last, usr, pwd, mail, id)
            accounts.append(acnt)

            response.add_cookie('client-id', id, 'Max-Age=604800', 'HttpOnly')  # 2 weeks
            response.add_cookie('validator', acnt.validator, 'Max-Age=604800', 'HttpOnly')

            response.set_status_code(303, location='account.html')

        elif reqadr[0] == 'pay.act':
            sender_id = client_id

            if not all(flags.values()):
                error = self.throwError(13, 'c', get_last(), response=response)
                self.log.log(addr[0], '- Client POSTed empty values.', lvl=Log.ERROR)
                return
            elif get_account_by_id(flags['recp']).blacklisted:
                error = self.throwError(14, 'b', get_last(), response=response)
                self.log.log(addr[0], '- Client tried to pay banned account.', lvl=Log.ERROR)
                return

            recipient_id = flags['recp']
            try:
                amount = int(flags['amt'])
            except ValueError:
                amount = float(flags['amt'])
            recipient_acnt = get_account_by_id(recipient_id)
            if recipient_acnt.shell:
                error = self.throwError(6, 'a', get_last(), response=response)
                self.log.log(addr[0], '- Client gave an invalid account id.', lvl=Log.ERROR)
                return
            a = client
            ar = recipient_acnt

            if not a.pay(amount, recipient_acnt):
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
                error = self.throwError(3, 'a', get_last(), response=response)
                self.log.log(addr[0], '- Client tried to overdraft.', lvl=Log.ERROR)
                return

        elif reqadr[0] == 'message.act':
            if not all(flags.values()):
                error = self.throwError(13, 'd', get_last(), response=response)
                self.log.log(addr[0], '- Client POSTed empty values.', lvl=Log.ERROR)
                return

            elif get_account_by_id(flags['recp']).blacklisted:
                error = self.throwError(14, 'c', get_last(), response=response)
                self.log.log(addr[0], '- Client tried to message banned account.', lvl=Log.ERROR)
                return

            recipient = get_account_by_id(flags['recp'])
            if recipient.shell:
                error = self.throwError(6, 'b', get_last(), response=response)
                self.log.log(addr[0], '- Client tried to message non-existent account.', lvl=Log.ERROR)
                return

            msg = flags['msg']
            subject = flags['subject']
            client.send_message(subject, msg, recipient)

            response.set_status_code(303, location="messages.html")

    error = ''
    if reqadr[-1].split('.')[-1] in ('html', 'htm'):
        response.add_cookie('page', '/'.join(reqadr))
    self.send(response)
    conn.close()

s = Server(localhost=True, debug=True, include_debug_level=False)
s.set_request_handler(handle)
s.open()
save_users()
