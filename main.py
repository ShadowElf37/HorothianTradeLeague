#!/usr/bin/env python3
"""
main.py
Project Mercury
Yovel Key-Cohen & Alwinfy
"""

from lib.server.server import *
from lib.server.log import *
from lib.server.response import *
from lib.account import *
from lib.boilerplate import *
from lib.bootstrapper import *
import lib.bootstrapper
import random
from threading import Thread


# Config
require_validator = True
log_request = True
log_transactions = False
log_signin = True
log_signup = True
log_request_flags = False

# Watcher for cmd.py - upon change of contents, runs file
Thread(target=infinite_file).start()

# Initializes the important things
whitelist = open('conf/whitelist.cfg', 'r').read().split('\n')
accounts, groups = load_users()
lib.bootstrapper.accounts = accounts  # Not sure why this is necessary, but the funcs in there can't handle main's vars
lib.bootstrapper.groups = groups
error = ''

# ---------------------------------

def handle(self, conn, addr, request):
    global error

    # Log request
    if log_request or request.file_type in ('html', 'htm', 'act'):
        self.log.log("Request from ", addr[0], ":", [request.method, request.address, request.cookies] + ([request.flags,] if log_request_flags else []) + [request.post_values,])

    # Finds the client by cookie, creates a response to modify later
    response = Response()
    client_id = request.get_cookie('client-id')
    client = get_account_by_id(client_id)
    client.ip_addresses.add(addr[0])
    response.logged_in = not client.shell

    # Default render values - these are input automatically to renders
    global host, port
    render_defaults = {'error':error, 'number_of_messages':len(list(filter(lambda x: not x.read, client.messages))), 'host':host, 'port':port, 'username':client.username, 'id':client_id, 'hunt_total':client.total_hunts, 'hunt_count':client.active_hunts, 'balance':client.balance}
    response.default_renderopts = render_defaults

    # Make sure client has a cookie and that it's valid - activity time is recorded
    if client_id is None:
        response.add_cookie('client-id', 'none')
    elif request.get_cookie('validator') != client.validator and response.logged_in and require_validator:
        response.add_cookie('client-id', 'none')
        response.add_cookie('validator', 'none')
        response.logged_in = False
        error = self.throwError(5, 'a', '/login.html', response=response)
        self.log.log(addr[0], '- Client\'s cookies don\'t match.', lvl=Log.ERROR)
        return
    elif response.logged_in:
        client.last_activity = time.strftime('%X (%x)')

    # Off to the request handling!
    if request.method == "GET":
        if request.address[0] == '':
            response.set_status_code(307, location='/home.html')
        elif request.address[0] == 'home.html':
            if client_id == 'none':
                response.attach_file('home.html')
            else:
                response.set_status_code(307, location='/news.html')

        elif request.address[0] == 'news.html':
            response.attach_file('news.html', nb_page='home.html')

        elif request.address[0] == 'treaty.html':
            response.set_body(client_error_msg('For those of you here in the closed beta: YOU CAN\'T TELL ANYONE ABOUT THIS.\
            <br>Don\'t even mention money or trades with other people around. This isn\'t the time for public advertisement.'))
            # response.set_status_code(307, location='https://drive.google.com/open?id=1vylaFRMUhj0fCGqDVhn0RC7xXmOegabodKs9YK-8zbs')

        elif request.address[0] == 'account.html':
            account = get_account_by_id(client_id)
            if not account.shell:
                response.attach_file('account.html')
            else:
                response.set_status_code(307, location='/login.html')

        elif request.address[0] == 'login.html':
            response.attach_file('login.html', nb_page="account.html")

        elif request.address[0] == 'pay.html':
            response.attach_file('pay.html', nb_page='account.html')

        elif request.address[0] == 'signup.html':
            response.attach_file('signup.html', nb_page='account.html')

        elif request.address[0] == 'transaction_history.html':
            cid = client_id
            acnt = get_account_by_id(cid)
            hist = []
            for item in acnt.transaction_history:
                item = item.split('|')
                #.format(amount, taxed, tid, time.strftime('%X - %x')))
                hist.append('<tr>'+''.join(tuple(map(td_wrap, item)))+'\n</tr>')
            response.attach_file('transaction_history.html', nb_page='account.html', history='\n'.join(hist))

        elif request.address[0] == 'registry.html':
            acnts = []
            for a in sorted(accounts, key=lambda u: u.lastname if not u.admin else u.id):
                acnts.append('<tr>' + td_wrap(a.firstname + ' ' + a.lastname) + td_wrap(a.id) + td_wrap(a.coalition.name) + td_wrap(a.last_activity) + td_wrap(a.date_of_creation) + '\n</tr>')
            response.attach_file('registry.html', nb_page='account.html', accounts='\n'.join(acnts))

        elif request.address[0] == 'messages.html':
            messages = []
            for msg in sorted(client.messages, key=lambda m: -float(m.sort_date)):
                m = '<div onmouseleave="mouseLeave(this)" onmouseover="updateMessage(\'{0}\', this)" class="preview" id="{0}">\n<span class="sender">{1}</span><br>\n<span class="subject">{2}</span>\n<span class="date">{3}</span>\n</div>'.format(
                    msg.id,
                    msg.sender.get_name(),
                    msg.subject.title() if msg.subject else 'No Subject',
                    msg.formal_date
                    )
                messages.append(m)
            if not messages:
                messages.append('<span class="no-message">Inbox empty...</span>')
            response.attach_file('messages.html', nb_page='account.html', messages='\n'.join(messages))

        elif request.address[0] == 'progress.html':
            f = open('conf/progress.cfg', 'r').readlines()
            for l in range(len(f)):
                f[l] = f[l].replace('%m%', str(len(list(filter(lambda a: not a.admin, accounts)))))

            lines = []
            compose = []
            for line in f:
                if line[0].strip() not in ('#', ''):
                    lines.append(tuple(map(lambda x: x.strip(), line.split(':'))))

            for line in lines:
                compose.append('<h3>' + line[0] + '</h3>' + '<div class="prog-bar"><div class="{2}" style="width: {0}"><span class="prog-bar-int-text">{1}</span></div></div><br>'.format(
                    str(100*eval(line[1])) + '%',
                    (line[1] if len(line) == 2 else line[2]) if eval(line[1]) < 1 else "Complete",
                    "prog-bar-int" if eval(line[1]) < 1 else "prog-bar-int-comp",

                    ))

            response.attach_file('progress.html', bars='\n'.join(compose))

        elif request.address[0] == 'settings.html':
            settings = open('conf/client_settings.cfg', 'r').read()
            fields = []
            for line in settings.split('\n'):
                if line != '' and line[0] != '#' and line[:4] != '<br>' and line[:2] != 'h.':
                    opts = line.split('|')
                    field = "<span class=\"desc-text\">{2}</span><input type=\"{0}\" name=\"{1}\" {3}>".format(*opts)
                    fields.append(field)
                elif line[:2] == 'h.':
                    fields.append("<h4>{}</h4>".format(line[2:]))
                elif line[:4] == '<br>':
                    fields.append('<br>'*int(line[4:]))

            response.attach_file('settings.html', settings='<br>\n'.join(fields), nb_page="account.html")

        elif request.address[0] == 'coalitions.html':
            if not client.coalition.default:
                response.set_status_code(303, location='coalition.html')
            else:
                response.set_status_code(303, location='coalition_list.html')

        elif request.address[0] == 'coalition_list.html':
                coalitions = []
                for group in groups:
                    if not group.exists:
                        continue
                    coalitions.append("""<a href="/c/{0}.{7}">
                    <div class="c-listing">
                        <img src="{1}">
                        <div class="white-back"></div>
                        <h4>{2}</h4><br>
                        <p>
                            Members: {3}<br>
                            Type: {4}<br>
                            Created: {5}<br>
                            Owner: {6}<br>
                            Coalit. ID: {0}
                        </p>
                    </div>
                </a>""".format(
                        group.cid,
                        group.img,
                        group.name,
                        str(len(group.members)),
                        "Guild" if isinstance(group, Guild) else "Coalition",
                        group.creation_date,
                        group.founder.get_name(),
                        'gld' if isinstance(group, Guild) else 'clt' if isinstance(group, Coalition) else 'std'
                    ))
                response.attach_file('coalition_list.html', groups='\n'.join(coalitions), nb_page='account.html')

        elif request.address[0] == 'coalition.html':
            c = 'clt' if isinstance(client.coalition, Coalition) else 'gld' if isinstance(client.coalition, Guild) else 'std'
            response.set_status_code(303, location='/c/'+client.coalition.cid+'.'+c)

        elif request.address[0] == 'create_coalition.html':
            img_opts = open('conf/clt_img.cfg').read().split('\n')
            opts = ['<option value="{}">{}</option>'.format(*line.split('|')) for line in img_opts]
            response.attach_file('create_coalition.html', nb_page='account.html', img_opts='\n'.join(list(opts)))

        # ACTIONS
        elif request.address[0].split('.')[-1] == 'act':
            if request.address[0] == 'logout.act':
                response.add_cookie('client-id', 'none')
                response.add_cookie('validator', 'none')
                response.set_status_code(303, location='home.html')
            elif request.address[0] == 'shutdown_normal.act':
                self.log.log('Initiating server shutdown...')
                self.close()
                lib.bootstrapper.running = False
                lib.bootstrapper.accounts = accounts
                lib.bootstrapper.groups = groups
                save_users()
                exit()
            elif request.address[0] == 'shutdown_force.act':
                lib.bootstrapper.running = False
                exit()
            elif request.address[0] == 'del_msg.act':
                client = get_account_by_id(request.address[2])
                try:
                    msg = next( m for m in client.messages if m.id == request.address[1] )
                    client.messages.remove(msg)
                except StopIteration:
                    self.log.log(addr[0], '- Client tried to delete non-existant message.')
                response.body = "Success"
            else:
                # Proper error handling
                error = self.throwError(2, 'a', request.get_last_page(), response=response)
                self.log.log(addr[0], '- Client requested non-existent action.', lvl=Log.ERROR)
                return

        elif request.address[0] == 'c':
            id, type = request.address[-1].split('.')
            li = lambda x: '<li>' + x + '</li>'

            if type == 'clt':
                try:
                    coalition = next(i for i in groups if i.cid == id)
                except StopIteration:
                    error = self.throwError(1, 'a', '/' + request.get_last_page(), response=response)
                    self.log.log(addr[0], '- Client requested non-existent coalition', lvl=Log.ERROR)
                    return

                response.attach_file('coalition.html',
                                     members='\n'.join(tuple(map(lambda x: li(x.get_name()), coalition.members))),
                                     c_id=coalition.cid,
                                     c_desc=coalition.description,
                                     c_owner=coalition.owner.get_name(),
                                     coalition_name=coalition.name,
                                     pool=coalition.pool,
                                     max_pool=coalition.max_pool,
                                     pct_loan=100 * coalition.get_loan_size(),
                                     amt_loan='%.2f' % float(coalition.get_loan_size() * coalition.max_pool),
                                     nb_page='account.html')
            elif type == 'gld':
                try:
                    coalition = next(i for i in groups if i.cid == id)
                except StopIteration:
                    error = self.throwError(1, 'b', '/' + request.get_last_page(), response=response)
                    self.log.log(addr[0], '- Client requested non-existent coalition', lvl=Log.ERROR)
                    return

                response.attach_file('guild.html',
                                     coalition_name=coalition.name,
                                     members='\n'.join(tuple(map(lambda x: li(x.get_name()), coalition.members))),
                                     c_id=coalition.cid,
                                     c_desc=coalition.description,
                                     c_owner=coalition.owner.get_name(),
                                     nb_page='account.html')
            elif type == 'std':
                error = self.throwError(15, 'a', request.get_last_page(), response=response)
                self.log.log(addr[0], '- Client requested a non-coalition coalition page (like Group() instance)', lvl=Log.ERROR)
                return
            else:
                response.set_status_code(303, location='/' + '/'.join(request.address[1:]))

        # MESSAGE FILES
        elif request.address[0] == 'm':
            try:
                # Open message, ignore metadata first line
                d = open('data/messages/' + request.address[1] + '.msg', 'r').read()
                head = d.split('\n')[0]
                id = head[head.find('->')+2:head.find(' |')].strip()
                d = '\n'.join(d.split('\n')[1:])
                # Set message to read for account.html message button rendering
                client = get_account_by_id(id)
                try:
                    msg = next( m for m in client.messages if m.id == request.address[1] )
                except StopIteration:
                    print('@', [m.id for m in client.messages])
                    print('!', client.id)
                    print('$', id)
                    print('#', request.address[1])
                    self.log.log(addr[0], "- SOMETHING VERY BAD HAPPENED IN MESSAGE FETCH")
                    return
                msg.read = True

                d = post_to_html_escape(d)

                response.body = d
            except FileNotFoundError:
                response.body = "|ERR|"
                self.log.log(addr[0], '- Client requested non-existent message file.', lvl=Log.ERROR)

        # --THIS HANDLES EXTRANEOUS REQUESTS--
        # --PLEASE AVOID BY SPECIFYING MANUAL HANDLE CONDITIONS--
        # --INTENDED FOR IMAGES AND OTHER RESOURCES--
        else:
            response.attach_file(request.address[0], rendr=True, rendrtypes=('html', 'htm', 'js', 'css'), nb_page=request.address[0])

    elif request.method == "POST":
        if not request.post_values:
            error = self.throwError(0, 'b', request.get_last_page(), response=response)
            self.log.log(addr[0], '- That thing happened again... sigh.', lvl=Log.ERROR)
            return

        if request.address[0] == 'login.act':
            usr = request.post_values['user']
            pwd = request.post_values['pass']
            u = get_account_by_username(usr)

            if not all(request.post_values.values()):
                error = self.throwError(13, 'a', request.get_last_page(), response=response)
                self.log.log(addr[0], '- Client POSTed empty values.', lvl=Log.ERROR)
                return
            elif u.blacklisted or addr[0] in open('data/banned_ip.dat').readlines():
                error = self.throwError(14, 'a', request.get_last_page(), response=response)
                self.log.log(addr[0], '- Client tried to log in to banned account.', lvl=Log.ERROR)
                return

            try:
                acnt = list(filter(lambda u: u.username == usr and u.password == pwd, accounts))[0]

                response.add_cookie('client-id', acnt.id, 'Max-Age=604800')  # 2 weeks
                response.add_cookie('validator', acnt.validator, 'Max-Age=604800', 'HttpOnly')

                response.set_status_code(303, location='account.html')
                if log_signin: self.log.log('Log in:', u.id)
            except IndexError:
                error = self.throwError(4, 'a', request.get_last_page(), response=response)
                self.log.log(addr[0], '- Client entered incorrect login information.', lvl=Log.ERROR)
                return

        elif request.address[0] == 'signup.act':
            first = request.post_values['first']
            last = request.post_values['last']
            mail = request.post_values['mail']
            usr = request.post_values['user']
            pwd = request.post_values['pass']
            cpwd = request.post_values['cpass']  # confirm password

            if not all(request.post_values.values()):
                error = self.throwError(13, 'b', request.get_last_page(), response=response)
                self.log.log(addr[0], '- Client POSTed empty values.', lvl=Log.ERROR)
                return

            elif not get_account_by_name(first, last).shell:
                error = self.throwError(8, 'a', request.get_last_page(), response=response)
                self.log.log(addr[0], '- Client tried to sign up with already-used name.', lvl=Log.ERROR)
                return

            elif not get_account_by_username(usr).shell:
                error = self.throwError(9, 'a', request.get_last_page(), response=response)
                self.log.log(addr[0], '- Client tried to sign up with already-used username.', lvl=Log.ERROR)
                return

            elif not first+' '+last in whitelist:
                error = self.throwError(10, 'a', request.get_last_page(), response=response)
                self.log.log(addr[0], '- Forbidden signup attempt.', lvl=Log.ERROR)
                return

            elif not get_account_by_email(mail):
                error = self.throwError(12, 'a', request.get_last_page(), response=response)
                self.log.log(addr[0], '- Client tried to sign up with already-used email.', lvl=Log.ERROR)
                return

            elif cpwd != pwd:
                error = self.throwError(7, 'a', request.get_last_page(), response=response)
                self.log.log(addr[0], '- Client pwd does not equal confirm pwd.', lvl=Log.ERROR)
                return

            id = '0000'
            while id in ('1377',) or id[:2] == '00' or not get_account_by_id(id).shell:  # Saving first 100 accounts for admin purposes
                id = '%04d' % random.randint(0, 9999)
                self.log.log("New account created with ID", id, "- first name is", first)
            acnt = Account(first, last, usr, pwd, mail, id)
            groups[0].add_member(acnt)
            accounts.append(acnt)

            response.add_cookie('client-id', id, 'Max-Age=604800')  # 2 weeks
            response.add_cookie('validator', acnt.validator, 'Max-Age=604800', 'HttpOnly')

            response.set_status_code(303, location='account.html')
            if log_signup: self.log.log('Sign up:', acnt.get_name(), acnt.id)

        elif request.address[0] == 'pay.act':
            sender_id = client_id

            if not all(request.post_values.values()):
                error = self.throwError(13, 'c', request.get_last_page(), response=response)
                self.log.log(addr[0], '- Client POSTed empty values.', lvl=Log.ERROR)
                return
            elif get_account_by_id(request.post_values['recp']).blacklisted:
                error = self.throwError(14, 'b', request.get_last_page(), response=response)
                self.log.log(addr[0], '- Client tried to pay banned account.', lvl=Log.ERROR)
                return

            recipient_id = request.post_values['recp']
            try:
                amount = int(request.post_values['amt'])
            except ValueError:
                amount = float(request.post_values['amt'])
            recipient_acnt = get_account_by_id(recipient_id)
            if recipient_acnt.shell:
                error = self.throwError(6, 'a', request.get_last_page(), response=response)
                self.log.log(addr[0], '- Client gave an invalid account id.', lvl=Log.ERROR)
                return
            a = client
            ar = recipient_acnt
            tax = a.coalition.internal_tax if a.coalition == ar.coalition else a.coalition.tax
            taxed = tax * amount
            amount -= taxed

            if not a.pay(amount, recipient_acnt):
                response.set_status_code(303, location='account.html')
                tid = '%19d' % random.randint(1, 2**64)
                f = open('logs/transactions.log', 'at')
                gl = '{0} -> {1}; Cr{2} [-{3}] ({4}) -- {5}\n'.format(sender_id, recipient_id, '%.2f' % amount, '%.2f' % taxed if taxed != 0 else 'EXEMPT', tid, time.strftime('%X - %x'))
                f.write(gl)
                if log_transactions: self.log.log('Transaction:', gl)
                a.transaction_history.append('&#8354;{0} sent to {1}|&#8354;{2}|3{3}|{4}'.format('%.2f' % amount, ar.get_name(), '%.2f' % taxed if taxed != 0 else 'EXEMPT', tid, time.strftime('%X - %x')))
                if a.id != '1377':
                    ar.transaction_history.append('{0} sent you &#8354;{1}|&#8354;{2}|2{3}|{4}'.format(a.get_name(), '%.2f' % amount, '%.2f' % taxed if taxed != 0 else 'EXEMPT', tid, time.strftime('%X - %x')))
                else:
                    ar.transaction_history.append('CB income of &#8354;{0}|&#8354;{1}|7{2}|{3}'.format('%.2f' % amount, '%.2f' % taxed if taxed != 0 else 'EXEMPT', tid, time.strftime('%X - %x')))
                f.close()
                get_account_by_id('1377').pay(float(taxed), get_account_by_id('0099'))
                get_account_by_id('0099').transaction_history.append('Tax income of &#8354;{0} from {1} -> {2}|EXEMPT|7{3}|{4}'.format('%.2f' % taxed, a.get_name(), ar.get_name(), tid, time.strftime('%X - %x')))
            else:
                error = self.throwError(3, 'a', request.get_last_page(), response=response)
                self.log.log(addr[0], '- Client tried to overdraft.', lvl=Log.ERROR)
                return

        elif request.address[0] == 'message.act':
            if not all(request.post_values.values()):
                error = self.throwError(13, 'd', request.get_last_page(), response=response)
                self.log.log(addr[0], '- Client POSTed empty values.', lvl=Log.ERROR)
                return

            elif get_account_by_id(request.post_values['recp']).blacklisted:
                error = self.throwError(14, 'c', request.get_last_page(), response=response)
                self.log.log(addr[0], '- Client tried to message banned account.', lvl=Log.ERROR)
                return

            recipient = get_account_by_id(request.post_values['recp'])
            if recipient.shell:
                error = self.throwError(6, 'b', request.get_last_page(), response=response)
                self.log.log(addr[0], '- Client tried to message non-existent account.', lvl=Log.ERROR)
                return

            msg = request.post_values['msg']
            subject = request.post_values['subject']
            client.send_message(subject, msg, recipient)

            response.set_status_code(303, location="messages.html")

        elif request.address[0] == 'save_settings.act':
            old_pwd = request.post_values['old-pwd']
            new_pwd = request.post_values['new-pwd']
            cnew_pwd = request.post_values['cnew-pwd']
            new_usr = request.post_values['new-usr']

            # This nall() thing is neat - like XOR but for a list
            if not nall(old_pwd, new_pwd, cnew_pwd) or not nall(new_usr,):
                error = self.throwError(13, 'e', request.get_last_page(), response=response)
                self.log.log(addr[0], '- Client failed to complete a settings form-group.', lvl=Log.ERROR)
                return

            if old_pwd:
                if new_pwd != cnew_pwd:
                    error = self.throwError(7, 'b', request.get_last_page(), response=response)
                    self.log.log(addr[0], '- Client pwd does not equal confirm pwd (settings).', lvl=Log.ERROR)
                    return
                if old_pwd == client.password:
                    client.password = new_pwd
                else:
                    error = self.throwError(4, 'b', request.get_last_page(), response=response)
                    self.log.log(addr[0], '- Client pwd incorrect (settings).', lvl=Log.ERROR)
                    return

            if new_usr:
                client.username = new_usr

            response.set_status_code(303, location='account.html')

        elif request.address[0] == 'create_coalition.act':
            name = post_to_html_escape(request.post_values['name'].replace('+', ' '))
            type = request.post_values['type']
            img = request.post_values['img']
            desc = post_to_html_escape(request.post_values['desc'].replace('+', ' '))

            if not all(request.post_values.values()):
                error = self.throwError(13, 'f', request.get_last_page(), response=response)
                self.log.log(addr[0], '- Client POSTed empty values.', lvl=Log.ERROR)
                return

            client.coalition.remove_member(client)
            if client.coalition.owner == client and client.coalition != groups[0]:
                client.coalition.dismantle(groups[0])
            if type == 'c':
                new = Coalition(name, img, client, desc)
            else:
                new = Guild(name, img, client, desc)

            groups.append(new)
            response.set_status_code(303, location="coalition.html")



    # Adds an error, sets page cookie (that thing that lets you go back if error), and sends the response off
    error = ''
    if request.address[-1].split('.')[-1] in ('html', 'htm'):
        response.add_cookie('page', '/'.join(request.address))
    self.send(response)
    conn.close()


# TURN DEBUG OFF FOR ALL REAL-WORLD TRIALS OR ANY ERROR WILL CAUSE A CRASH
# USE SHUTDOWN URLs TO TURN OFF

host = '192.168.1.177'
port = 8080
s = Server(host=host, port=port, debug=True, include_debug_level=False)
s.log.log('Accounts:', accounts, lvl=Log.INFO)
s.log.log('Groups:', groups, lvl=Log.INFO)
s.set_request_handler(handle)
s.open()
save_users()
lib.bootstrapper.running = False
