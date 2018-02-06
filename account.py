"""
account.py
Project Mercury
Yovel Key-Cohen
"""

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
    def __add__(self, other):
        return 2 ** 64
    def __sub__(self, other):
        return 2 ** 64
    def __mul__(self, other):
        return 2**64
    def __str__(self):
        return '∞'


class Account:
    def __init__(self, firstname, lastname, username, password, id):
        self.id = id
        self._balance = 0
        self.username = username
        self.password = password
        self.firstname = firstname
        self.lastname = lastname
        self.coalition = 'none'
        self.transaction_history = []

    @property
    def balance(self):
        return self._balance if self.id != '1377' else Infinity()

    @balance.setter
    def balance(self, val):
        self._balance = val

    def pay(self, amt, account):
        if amt <= self.balance:
            account.balance += amt
            if self.id != '1377':
                self.balance -= amt
            self.balance = float('%.2f' % self.balance)
            return 0
        else:
            return 1
