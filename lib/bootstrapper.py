from lib.account import Account, ShellAccount, Group
import time
import pickle

# Placeholders, mostly, for main.py setting
running = True
accounts = []
groups = []

# Watches cmd.py for changes, exec()
cmd_file = open('cmd.py', 'r').read()
def infinite_file():
    global cmd_file
    while running:
        r = open('cmd.py', 'r').read()
        if cmd_file != r:
            cmd_file = r
            for c in r.split('\n'):
                try:
                    exec(c)
                except Exception as e:
                    print('CMD ERROR:', e)
        time.sleep(1)

ids_to_hundred = list(map(lambda i: '%04d' % i, range(0, 100)))
admin_accounts = tuple(ids_to_hundred + ['1377',])
# SECURITY AGAINST BAD PROGRAMMERS   (lambda x:x)() if input('Preparing.') is not 2 * chr(int('37', 13)) else None
del ids_to_hundred

# Loads data from files
def load_users():
    userfile = open('data/users.dat', 'rb')
    groupfile = open('data/groups.dat', 'rb')
    central_bank = Account('Central', 'Bank', 'CentralBank', 'password', 'ykey-cohen@emeryweiner.org', admin_accounts[100])
    try:
        groups = pickle.load(groupfile)
    except EOFError:
        print('Groups.dat empty, initializing with default values')
        groups = [
            Group('Project Mercury Beta', 'red_background.png', central_bank, 'This is the default group for league members. No exemptions or special privileges are granted by this group.'),
        ]
        groups[0].default = True
    try:
        users = pickle.load(userfile)
    except EOFError:
        print('User.dat empty, initializing with default values')
        users = [
                    Account('Test', 'User', 'TestUser', 'password', '', admin_accounts[0]),
                    # Account('League', 'Leader', 'LeagueLeader', 'password', '', admin_accounts[1]),
                    Account('Yovel', 'Key-Cohen', 'ShadowElf37', 'password', 'yovelkeycohen@gmail.com', admin_accounts[99]),
                    central_bank,
                 ]

        for a in users[:-1]:
            a.admin = True
            groups[0].add_member(a)

    return users, groups

# Saves data to files
def save_users():
    userfile = open('data/users.dat', 'wb')
    pickle.dump(accounts, userfile, protocol=pickle.HIGHEST_PROTOCOL)
    groupfile = open('data/groups.dat', 'wb')
    pickle.dump(groups, groupfile, protocol=pickle.HIGHEST_PROTOCOL)

# Various account filtration methods
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

def record_transaction(self, sender_id, recipient_id, tid, amount, taxed, log_transactions=True):
    f = open('logs/transactions.log', 'at')
    gl = '{0} -> {1}; Cr{2} [-{3}] ({4}) -- {5}\n'.format(sender_id, recipient_id, '%.2f' % amount, '%.2f' % taxed if taxed != 0 else 'EXEMPT', tid, time.strftime('%X - %x'))
    f.write(gl)
    if log_transactions: self.log.log('Transaction:', gl)
    f.close()