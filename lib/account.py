"""
account.py
Project Mercury
Yovel Key-Cohen
"""

import random
import time
from lib import encrypt
from lib import boilerplate


class Infinity:
    def __int__(self):
        return 2**64
    def __float__(self):
        return 2.0**64
    def __gt__(self, *args):
        return True
    def __ge__(self, *args):
        return True
    def __lt__(self, *args):
        return False
    def __le__(self, *args):
        return False
    def __eq__(self, *args):
        return False
    def __add__(self, other):
        return 2 ** 64
    def __sub__(self, other):
        return 2 ** 64
    def __mul__(self, other):
        return 2 ** 64
    def __str__(self):
        return '∞'


class Sale:
    def __init__(self, seller, cost, name, img):
        self.cost = cost
        self.name = name
        self.img = img
        self.sold = False
        self.seller = seller
        self.buyer = ShellAccount()
        self.id = str(random.randint(10**8, 10**9))
        self.guild = ''
        self.posted_date = time.strftime('%x')
        

class Message:
    def __init__(self, subject, msg, sender, recipient):
        self.msg = msg
        self.formal_date = time.strftime('%m/%d/%y<br>%I:%M %p')
        self.sort_date = str(time.time())
        self.id = '%08d' % random.randint(10**8, 10**9-1)
        self.sender = sender
        self.recipient = recipient
        self.subject = subject.replace('+', ' ')
        self.read = False

        self.file = open("data/messages/"+self.id+".msg", 'w')
        h = '# ' + self.sender.id + ' -> ' + self.recipient.id + ' | ' + self.formal_date + '\n'
        self.file.write(h + self.msg.replace('+', ' '))
        self.file.close()


class Hunt:
    def __init__(self, creator, title, description, deadline, max_contributors, reward, link):
        self.title = title
        self.desc = description
        self.due_date = deadline
        self.posted_date = time.strftime('%x')
        self.max_contributors = max_contributors
        self.reward = float(reward)
        self.total_reward = self.max_contributors * self.reward
        self.id = '%5d' % random.randint(10000, 99999)
        self.creator = creator
        self.complete = False
        self.participants = []
        self.completers = []
        self.paid = []
        self.link = link
        self.participant_ids = dict()

    def join(self, acnt):
        if len(self.participants) + len(self.completers) < self.max_contributors:
            self.participants.append(acnt)
            acnt.working_hunts.append(self)
            get_account_by_id('1377').send_message('Hunt: ' + self.title, acnt.get_name()+' has joined your hunt!', self.creator)
            self.participant_ids[str(random.randint(1000000, 10000000))] = acnt
            return 0
        return 1

    def finish(self, acnt):
        self.completers.append(acnt)
        self.participants.remove(acnt)

    def end(self):
        if not self.complete:
            self.complete = True
            for p in self.completers:
                p.working_hunts.remove(self)
                leftover = self.total_reward - (self.reward * len(self.completers))
                get_account_by_id('1377').pay(leftover, self.creator)


class Account:
    def __init__(self, firstname, lastname, username, password, email, id):
        self.id = id
        self._balance = 0
        self.username = username
        self._password = encrypt.encrypt(password, 'c')
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.coalition = None
        self.session_id = 'none'
        self.transaction_history = []
        self.messages = []
        self.sent_messages = []
        self.shell = False
        self.validator = self.get_new_validator()
        self.total_hunts = 0
        self.active_hunts = 0
        self.my_hunts = []
        self.working_hunts = []
        self.last_activity = 'Unused'
        self.date_of_creation = time.strftime('%c')
        self.admin = False
        self.blacklisted = False
        self.ip_addresses = set()
        self.settings = {}
        self.requested_coalition = False
        self.coal_pct_loaned = 0.0
        self.signup_data = dict()
        self.my_sales = []

    @property
    def password(self):
        return encrypt.decrypt(self._password, 'c')

    @password.setter
    def password(self, val):
        self._password = encrypt.encrypt(val, 'c')


    @property
    def balance(self):
        return self._balance if self.id != '1377' else Infinity()

    @balance.setter
    def balance(self, val):
        self._balance = round(val, 2)

    def pay(self, amt, account):
        if amt <= self.balance:
            account.balance += amt
            print('!!!', amt)
            if self.id != '1377':
                self.balance -= amt
            account.balance = float('%.2f' % account.balance)
            self.balance = float('%.2f' % self.balance)
            return 0
        return 1

    @staticmethod
    def get_new_validator():
        s = '%64d' % random.randint(10 ** 64, 10 ** 65 - 1)  # 512-bit validator
        return s

    def get_name(self):
        return self.firstname + ' ' + self.lastname

    def send_message(self, subject, msg, recpt):
        m = Message(subject, msg, self, recpt)
        self.sent_messages.append(m)
        recpt.messages.append(m)

    # Can be used for SID some time
    def compose_validator_string(self):
        return ''.join(list(map(lambda x: str(hex(ord(x) % 16)[2:]), encrypt.encrypt(self.validator, self.last_activity))))


class ShellAccount:
    def __init__(self):
        self.id = None
        self.balance = 0
        self.username = None
        self.password = None
        self.firstname = None
        self.lastname = None
        self.coalition = None
        self.session_id = 'none'
        self.transaction_history = []
        self.shell = True
        self.total_hunts = 0
        self.active_hunts = 0
        self.date_of_creation = 'none'
        self.admin = False
        self.email = 'none'
        self.blacklisted = False
        self.messages = []
        self.ip_addresses = set()
        self.settings = {}
        self.validator = None
        self.requested_coalition = False
        self.signup_data = dict()
        self.my_sales = []
        self.my_hunts = []


class Group:
    def __init__(self, name, img, founder, desc):
        self.tax = 0.05
        self.internal_tax = 0.05
        self.max_members = 5
        self.name = name
        self.members = []
        self.member_ids = []
        self.description = desc
        self.creation_date = time.strftime('%x')
        self.cid = str(random.randint(10**5, 10**6-1))
        self.img = img
        self.default = False
        self.founder = founder
        self.owner = founder
        self.add_member(founder)
        self.exists = True
        self.lost_members = []

    def add_member(self, account):
        if len(self.members) < self.max_members:
            self.members.append(account)
            self.member_ids.append(account.id)
            account.coalition = self
        else:
            return 'E0'

    def remove_member(self, account, default_group):
        self.members.remove(account)
        self.member_ids.remove(account.id)
        self.lost_members.append(account.id)
        if len(self.members) == 0:
            self.exists = False
        account.coalition = default_group

    def change_owner(self, new_account):
        self.owner = new_account

    def dismantle(self, default_group):
        for member in self.members:
            default_group.add_member(member)
        self.members = []
        self.exists = False

    def get_name(self):
        return self.name


class Coalition(Group):  # Get with your friends and make a living together
    def __init__(self, name, img, founder, desc):
        super().__init__(name, img, founder, desc)
        self.internal_tax = 0.0
        self.pool = 0.0
        self.max_pool = 0.0

    def get_loan_size(self):
        return boilerplate.cap(130 // (len(self.members)), 100) / 100.0

    def add_to_pool(self, amt, acnt):
        if acnt.balance >= amt:
            oldamt = self.max_pool
            acnt.balance -= amt
            self.pool += amt
            self.max_pool += amt
            for member in self.members:
                member.coal_pct_loaned = (member.coal_pct_loaned * oldamt) / self.max_pool
            return 0
        return 1

    def loan(self, amt, acnt):
        percent = amt / self.max_pool
        if percent + acnt.coal_pct_loaned <= 1.3/(len(self.members)):  # A user cannot loan more than 26% for 5 members etc.
            self.pool -= self.pool * percent
            acnt.coal_pct_loaned += percent
            acnt.balance += self.pool * percent
            return 0
        return 1

    def pay_loan(self, amt, acnt):
        percent = amt / self.max_pool
        self.pool += self.pool * percent
        acnt.coal_pct_loaned -= percent
        acnt.balance -= self.pool * percent
        return 0

# Join a guild and enjoy the benefits of capitalism!
# Note that payments to a Guild should ONLY go through a sales.html
class Guild(Group):
    def __init__(self, name, img, founder, desc):
        self.credit = dict()
        super().__init__(name, img, founder, desc)
        self.tax = 0.02
        self.max_members = 12
        self.std_salary = 1.0
        self.budget = 0.0

    def pay_member(self, amt, acnt):
        if self.budget > amt and acnt in self.members:
            self.budget -= amt
            self.credit[acnt] += amt
            return 0
        return 1

    def get_credit(self, acnt):
        acnt.balance += self.credit[acnt] - (self.credit[acnt] * self.tax)
        self.credit[acnt] = 0

    def add_member(self, account):
        if len(self.members) < self.max_members:
            self.members.append(account)
            self.member_ids.append(account.id)
            account.coalition = self
            self.credit[account] = 0.0
        else:
            return 'E0'

from lib.bootstrapper import get_account_by_id