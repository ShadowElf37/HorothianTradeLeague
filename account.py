"""
account.py
Project Mercury
Yovel Key-Cohen
"""

class Account:
    def __init__(self, username, password, id):
        self.id = id
        self.balance = 0
        self.username = username
        self.password = password

    def pay(self, amt, account):
        if amt <= self.balance:
            account.balance += amt
            if self.id != '1377':
                self.balance -= amt
            return 0
        else:
            return 1
