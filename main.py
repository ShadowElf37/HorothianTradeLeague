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
import datetime
from threading import Thread


# Config
require_validator = False
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
hunts = [h for a in accounts for h in a.my_hunts]
pm_group = groups[0]
lib.bootstrapper.accounts = accounts  # Not sure why this is necessary, but the funcs in there can't handle main's vars
lib.bootstrapper.groups = groups
error = ''
CB = get_account_by_id('1377')

test = Hunt(CB, 'HON English Essay Revision', 'I need someone to edit my essay for English please thanks.', '3/15/18', 5, 4, 'http://www.google.com/')
hunts.append(test)
CB.my_hunts.append(test)


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
                compose.append('<h3>' + line[0] + '</h3>' + '<div class="prog-bar"><div class="{2}" style="width: 0%" id="{3}"><script>move(document.getElementById("{3}"), {0});</script><span class="prog-bar-int-text">{1}</span></div></div><br>'.format(
                    str(100*eval(line[1])),
                    (line[1] if len(line) == 2 else line[2]) if eval(line[1]) < 1 else "Complete",
                    "prog-bar-int" if eval(line[1]) < 1 else "prog-bar-int-comp",
                    lines.index(line) + 100
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

        elif request.address[0] == 'clt_transfer_ownership.html':
            response.attach_file('clt_transfer_ownership.html', nb_page='account.html')

        elif request.address[0] == 'pay_member.html':
            mems = ['<option value="{}">{}</option>'.format(m.id, m.get_name()) for m in client.coalition.members]
            response.attach_file('pay_member.html', nb_page='account.html', clt_balance=client.coalition.budget, members='\n'.join(mems))

        elif request.address[0] == 'edit_coalition.html':
            mems = ['<li><input name="kick-mem" value="{}" type="checkbox" style="box-shadow: initial;">{}</li>'.format(m.id, m.get_name()) for m in client.coalition.members if m is not client.coalition.owner]
            img_opts = open('conf/clt_img.cfg').read().split('\n')
            opts = ['<option value="{}">{}</option>'.format(*line.split('|')) for line in img_opts]
            response.attach_file('edit_coalition.html', nb_page='account.html',
                                 i_members='\n'.join(mems),
                                 c_name=client.coalition.name,
                                 c_desc=client.coalition.description,
                                 img_opts='\n'.join(list(opts)))

        elif request.address[0] == 'clt_pooladd.html':
            c = client.coalition
            response.attach_file('clt_pooladd.html', nb_page='account.html', cpool='%.2f' % c.pool)

        elif request.address[0] == 'loan.html':
            c = client.coalition
            response.attach_file('loan.html', nb_page='account.html', ceiling=cap(c.max_pool * c.get_loan_size(), c.pool))
        elif request.address[0] == 'loan_view.js':
            response.attach_file('loan_view.js', loan_ceiling=client.coalition.max_pool)

        elif request.address[0] == 'hunts.html':
            l = []
            time_add = lambda start, add: (datetime.datetime.strptime(start, '%x') + datetime.timedelta(days=add)).strftime('%x')
            for h in hunts:
                if not h.complete and not (len(h.participants) / h.max_contributors >= 1):
                    l.append("""<a href="h-{4}"><div class="hunt">
                    <img class="hunt-img" src="google_doc.png">
                    <div class="dark-overlay"></div>
                    <div class="dark-bar {5}"></div>
                    <div class="dark-bar dark-bar-2">
                        <span class="title">{0}</span>
                        <span class="title author">Due {3}<br>{1}<br>Participants: {2}</span>
                    </div>
                </div></a>""".format(
                        h.title,
                        h.creator.get_name(),
                        '{}/{}'.format(len(h.participants), h.max_contributors) if not (len(h.participants) / h.max_contributors >= 1) else 'FULL',
                        h.due_date,
                        h.id,
                        'red' if (time.strftime('%x') in [time_add(h.due_date, -1), time_add(h.due_date, 0)]) else '',
                    ))
            response.attach_file('hunts.html', hunts='\n'.join(l))

        elif request.address[0] == 'my_hunts.html':
            response.attach_file('my_hunts.html', nb_page='hunts.html',
                                 phunts='\n'.join(['<li><a href="h-{1}">{0}</a></li>'.format(h.title, h.id) for h in client.working_hunts if not h.complete]),
                                 mhunts='\n'.join(['<li><a href="h-{1}">{0}</a></li>'.format(h.title, h.id) for h in client.my_hunts if not h.complete]))

        # HUNTS
        elif request.address[0][:2] == 'h-':
            num = request.address[0][2:]
            try:
                hunt = next(h for h in hunts if h.id == num)
            except StopIteration:
                error = self.throwError(1, 'c', request.get_last_page(), response=response)
                self.log.log(addr[0], '- Client requested non-existent hunt.', lvl=Log.ERROR)
                return

            response.attach_file('hunt.html', nb_page='hunts.html',
                                 hunt_name=hunt.title,
                                 creator=hunt.creator.get_name(),
                                 posted_date=hunt.posted_date,
                                 due_date=hunt.due_date,
                                 reward=hunt.reward,
                                 desc=hunt.desc,
                                 left=hunt.max_contributors - len(hunt.participants),
                                 claim_text='Claim Completion' if client in hunt.participants else 'Close Hunt' if client is hunt.creator else 'Claim Hunt',
                                 hunted='disabled' if client in hunt.completers else '',
                                 link='<a href="{}">Document Link</a>'.format(hunt.link) if client in hunt.participants+hunt.completers+[hunt.creator] else '',
                                 hid=hunt.id,
                                 )
        elif request.address[0][:3] == 'hp-':
            n, hid, tid = request.address[0].split('-')
            del n
            hunt = next(h for h in hunts if h.id == hid)
            acnt = hunt.participant_ids[tid]
            tax = hunt.reward * (hunt.creator.coalition.tax if not hunt.creator.coalition == acnt.coalition else hunt.creator.coalition.internal_tax)
            amt = hunt.reward - tax

            record_transaction(self, hunt.creator.id, client.id, '22' + str(random.randint(1000000, 10000000)),
                               amt, tax)
            CB.pay(amt, acnt)
            CB.pay(tax, get_account_by_id('0099'))
            response.set_status_code(303, location='hunts.html')


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

            elif request.address[0] == 'hunt_button.act':
                try:
                    hunt = next(h for h in hunts if h.id == request.address[1])
                except StopIteration:
                    error = self.throwError(2, 'b', request.get_last_page(), response=response)
                    self.log.log(addr[0], '- Client requested non-existent hunt.', lvl=Log.ERROR)
                    return

                if client in hunt.participants:  # Complete
                    hunt.finish(client)
                    tid = {v:k for k in hunt.participant_ids.keys() for v in hunt.participant_ids.values()}[client]
                    CB.send_message('Hunt: '+hunt.title,
                                    '{} claims that they\'ve completed the objective of {}. &#x7B;Click here&#x7C;/hp-'.format(client.get_name(), hunt.title)+hunt.id+'-'+tid+'&#x7D; to confirm that this is true and send them their reward.',
                                    hunt.creator)
                    response.set_status_code(303, location='/h-'+hunt.id)

                elif client is hunt.creator:  # End
                    hunt.end()
                    response.set_status_code(303, location='/hunts.html')
                else:  # Join
                    hunt.join(client)
                    response.set_status_code(303, location='/h-'+hunt.id)

            elif request.address[0] == 'del_msg.act':
                try:
                    msg = next( m for m in client.messages if m.id == request.address[1] )
                    client.messages.remove(msg)
                except StopIteration:
                    self.log.log(addr[0], '- Client tried to delete non-existant message.')
                response.body = "Success"
            elif request.address[0] == 'disband_coalition.act':
                client.coalition.dismantle(pm_group)
                response.set_status_code(303, location='coalitions.html')
            elif request.address[0] == 'collect_guild_salary.act':
                tid = '%19d' % random.randint(1, 2 ** 64)
                c = client.coalition.credit[client]
                taxed = c * client.coalition.internal_tax
                c = c - taxed
                client.transaction_history.append('Guild salary of &#8354;{0}|&#8354;{1}|9{2}|{3}'.format('%.2f' % c, '%.2f' % taxed, tid, time.strftime('%X - %x')))
                f = open('logs/transactions.log', 'at')
                gl = '{0} -> {1}; Cr{2} [-{3}] ({4}) -- {5}\n'.format(client.coalition.cid, client_id, '%.2f' % c, '%.2f' % taxed, tid, time.strftime('%X - %x'))
                f.write(gl)
                if log_transactions:
                    self.log.log(addr[0], '- Client collected guild salary of', c)
                client.coalition.get_credit(client)

                response.set_status_code(303, location='coalitions.html')
            elif request.address[0] == 'request_join.act':
                try:
                    coalition = next(i for i in groups if i.cid == request.address[1] and i.exists)
                except StopIteration:
                    print(request.address[1])
                    for c in groups:
                        print(c.cid)
                    return
                if not client.requested_coalition:
                    rid = str(random.randint(10**5, 10**6))
                    client.requested_coalition = True
                    f = open('data/clt_join_reqs.dat', 'w')
                    f.write('{}|{}|{}'.format(
                        client.id,
                        coalition.cid,
                        rid
                    ))
                    f.close()

                    get_account_by_id('1377').send_message('Join Coalition Request', 'Your request to join coalition {} is pending approval by the owner.'.format(coalition.cid), client)
                    get_account_by_id('1377').send_message('Join Coalition Request', '{} ({}) requested to join your coalition!\nYou can accept it by going to {this link.|http://{}:{}/accept_request.act/{}}'.format(
                        client.get_name(),
                        client.id,
                        host,
                        port,
                        rid
                    ),coalition.owner)

                    response.set_status_code(303, location="/coalitions.html")
            elif request.address[0] == 'accept_request.act':
                data = open('data/clt_join_reqs.dat', 'r').read().split('\n')
                try:
                    r = tuple(filter(lambda x: x.split('|')[2] == request.address[1], data))[0].split('|')
                except IndexError:
                    print("REALLY BAD ERROR")
                    self.send('Well that didn\'t work!')
                    return

                tuple(filter(lambda x: x.cid == r[1], groups))[0].add_member(get_account_by_id(r[0]))
                get_account_by_id('1377').send_message('Join Coalition Request',
                                                       'Your request to join the coalition was approved! You can access it with the COALITIONS button in your account.',
                                                       get_account_by_id(r[0]))

                response.set_status_code(303, location="/coalitions.html")
            elif request.address[0] == 'leave_coalition.act':
                client.coalition.remove_member(client, pm_group)
                if isinstance(client.coalition, Guild):
                    client.coalition.budget += client.coalition.credit[client]
                    client.coalition.credit[client] = 0
                response.set_status_code(303, location='coalitions.html')
            else:
                # Proper error handling
                error = self.throwError(2, 'a', request.get_last_page(), response=response)
                self.log.log(addr[0], '- Client requested non-existent action.', lvl=Log.ERROR)
                return

        elif request.address[0] == 'c':
            try:
                id, type = request.address[1].split('.')
                othertype = False
            except ValueError:
                othertype = True
            li = lambda x: '<li>' + x + '</li>'

            if not othertype and type == 'clt':
                try:
                    coalition = next(i for i in groups if i.cid == id and i.exists)
                except StopIteration:
                    error = self.throwError(1, 'a', '/' + request.get_last_page(), response=response)
                    self.log.log(addr[0], '- Client requested non-existent coalition', lvl=Log.ERROR)
                    return

                owner = coalition.owner is client
                member = client.coalition is coalition
                disabled = lambda condition: 'disabled' if condition else ''
                response.attach_file('coalition.html',
                                     members='\n'.join(tuple(map(lambda x: li(x.get_name()), coalition.members))),
                                     c_id=coalition.cid,
                                     c_desc=coalition.description,
                                     c_owner=coalition.owner.get_name(),
                                     coalition_name=coalition.name,
                                     pool='%.2f' % coalition.pool,
                                     max_pool='%.2f' % coalition.max_pool,
                                     pct_loan=100 * coalition.get_loan_size(),
                                     amt_loan='%.2f' % float(coalition.get_loan_size() * coalition.max_pool),
                                     pct_client_loan=('%.1f' % (client.coal_pct_loaned * 100)) if coalition == client.coalition else 'n/a',
                                     amt_client_loan=('%.2f' % (client.coal_pct_loaned * coalition.max_pool)) if coalition == client.coalition else 'n/a',

                                     disleave = 'disband_coalition.act' if owner else 'leave_coalition.act',
                                     disleavet = 'Disband' if owner else 'Leave',
                                     d1=disabled(member),
                                     d2=disabled(not owner),
                                     d3=disabled(not member),
                                     d4=disabled(not member),
                                     d5=disabled(not owner),
                                     d6=disabled(not member or not client.coal_pct_loaned > 0),
                                     nb_page='account.html')
            elif not othertype and type == 'gld':
                try:
                    coalition = next(i for i in groups if i.cid == id and i.exists)
                except StopIteration:
                    error = self.throwError(1, 'b', '/' + request.get_last_page(), response=response)
                    self.log.log(addr[0], '- Client requested non-existent coalition', lvl=Log.ERROR)
                    return

                owner = coalition.owner is client
                member = client.coalition is coalition
                disabled = lambda condition: 'disabled' if condition else ''
                if len(request.address) > 2:
                    if request.address[2] == 'budget.html':
                        response.attach_file('budget.html', nb_page='account.html',
                                             name=coalition.name,
                                             budget=coalition.budget,
                                             credit=coalition.credit[client]
                                             )
                    else:
                        response.set_status_code(303, location='/' + request.address[2])
                else:
                    response.attach_file('guild.html',
                                         coalition_name=coalition.name,
                                         members='\n'.join(tuple(map(lambda x: li(x.get_name()), coalition.members))),
                                         c_id=coalition.cid,
                                         c_desc=coalition.description,
                                         c_owner=coalition.owner.get_name(),

                                         disleave='disband_coalition.act' if owner else 'leave_coalition.act',
                                         disleavet='Disband' if owner else 'Leave',
                                         d1=disabled(member),
                                         d2=disabled(not owner),
                                         d3=disabled(not member),
                                         d4=disabled(not member),
                                         d5=disabled(not owner),
                                         d6=disabled(not owner),
                                         d7=disabled(not member),
                                         nb_page='account.html')
            elif othertype or type == 'std':
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
            pm_group.add_member(acnt)
            acnt.signup_data = request.post_values
            accounts.append(acnt)

            response.add_cookie('client-id', id, 'Max-Age=604800')  # 2 weeks
            response.add_cookie('validator', acnt.validator, 'Max-Age=604800', 'HttpOnly')

            response.set_status_code(303, location='account.html')
            if log_signup: self.log.log('Sign up:', acnt.get_name(), acnt.id)

        elif request.address[0] == 'pay.act':
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
                record_transaction(self, a, ar, tid, amount, taxed, log_transactions)
                a.transaction_history.append(
                    '&#8354;{0} sent to {1}|&#8354;{2}|3{3}|{4}'.format('%.2f' % amount, ar.get_name(),
                                                                        '%.2f' % taxed if taxed != 0 else 'EXEMPT', tid,
                                                                        time.strftime('%X - %x')))
                if a.id != '1377':
                    ar.transaction_history.append(
                        '{0} sent you &#8354;{1}|&#8354;{2}|2{3}|{4}'.format(a.get_name(), '%.2f' % amount,
                                                                             '%.2f' % taxed if taxed != 0 else 'EXEMPT',
                                                                             tid, time.strftime('%X - %x')))
                else:
                    ar.transaction_history.append('CB income of &#8354;{0}|&#8354;{1}|7{2}|{3}'.format('%.2f' % amount,
                                                                                                       '%.2f' % taxed if taxed != 0 else 'EXEMPT',
                                                                                                       tid,
                                                                                                       time.strftime(
                                                                                                           '%X - %x')))
                ar.pay(float(taxed), get_account_by_id('0099'))
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

            client.coalition.remove_member(client, pm_group)
            if client.coalition.owner == client and client.coalition != pm_group:
                client.coalition.dismantle(pm_group)
            if type == 'c':
                new = Coalition(name, img, client, desc)
            else:
                new = Guild(name, img, client, desc)

            groups.append(new)
            response.set_status_code(303, location="coalition.html")

        elif request.address[0] == 'transfer_ownership.act':
            if not all(request.post_values.values()):
                error = self.throwError(13, 'g', request.get_last_page(), response=response)
                self.log.log(addr[0], '- Client POSTed empty values.', lvl=Log.ERROR)
                return

            target = get_account_by_id(request.post_values.get('id'))
            if target == 'none':
                error = self.throwError(6, 'c', request.get_last_page(), response=response)
                self.log.log(addr[0], '- Client POSTed bad account ID.', lvl=Log.ERROR)
                return

            if target.coalition is client.coalition or target.coalition is pm_group:
                client.coalition.change_owner(target)
            else:
                error = self.throwError(16, 'a', request.get_last_page(), response=response)
                self.log.log(addr[0], '- Client tried to make a coalition owner the owner of a coalition.', lvl=Log.ERROR)
                return

            response.set_status_code(303, location='coalitions.html')

        elif request.address[0] == 'pay_member.act':
            if not all(request.post_values.values()):
                error = self.throwError(13, 'g', request.get_last_page(), response=response)
                self.log.log(addr[0], '- Client POSTed empty values.', lvl=Log.ERROR)
                return

            target = get_account_by_id(request.post_values.get('id'))
            if target == 'none':
                error = self.throwError(6, 'c', request.get_last_page(), response=response)
                self.log.log(addr[0], '- Client POSTed bad account ID.', lvl=Log.ERROR)
                return

            client.coalition.pay_member(float(request.post_values.get('amt')), target)
            response.set_status_code(303, location='coalitions.html')

        elif request.address[0] == 'edit_clt.act':
            c = client.coalition
            if request.post_values.get('name'):
                c.name = request.post_values['name']
            if request.post_values.get('desc'):
                c.description = request.post_values['desc']
            if request.post_values.get('img'):
                c.img = request.post_values['img']
            if request.post_values.get('kick-mem'):
                msg = 'The owner of your coalition decided to kick you out. If you think this was done unfairly, please submit an appeal to the Project Mercury Court. Keep in mind that the coalition is their property, not yours, and not ours.'
                km = request.post_values['kick-mem']
                self.log.log('Member kicked from a coalition by {}'.format(client.id))
                if isinstance(km, list):
                    for mem in km:
                        m = get_account_by_id(mem)
                        c.remove_member(m, pm_group)
                        get_account_by_id('1377').send_message('Coalition Kick', msg, m)
                else:
                    m = get_account_by_id(km)
                    c.remove_member(m, pm_group)
                    get_account_by_id('1377').send_message('Coalition Kick', msg, m)
            response.set_status_code(303, location='coalitions.html')

        elif request.address[0] == 'padd.act':
            c = client.coalition
            amt = float(request.post_values['amt'])
            client.transaction_history.append('')
            c.add_to_pool(amt, client)
            tid = random.randint(10**5, 10**6)
            client.transaction_history.append('&#8354;{0} donated to {1}|&#8354;{2}|3{3}|{4}'.format('%.2f' % amt, c.name, 'EXEMPT', tid, time.strftime('%X - %x')))
            record_transaction(self, client.id, c.cid, tid, amt, 0, log_transactions)
            response.set_status_code(303, location='coalitions.html')

        elif request.address[0] == 'loan.act':
            c = client.coalition
            amt = float(request.post_values['amt'])
            c.loan(amt, client)
            response.set_status_code(303, location="coalitions.html")


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
