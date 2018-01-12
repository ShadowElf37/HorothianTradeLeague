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
            else:  # a payment from the central bank, and thus a change in the economy
                fecn = open('economy.dat', 'w+')
                writebufffer = []
                for line in fecn.readlines():
                    l = line.split(':')
                    if l[0] == 'TotalCredits':
                        writebuffer.append((l[0], int(l[1]) + amt))
                writebuffer = '\n'.join(list(map(lambda x: ':'.join(x), writebuffer)))
                fecn.write(writebuffer)
                fecn.close()
            return 0
        else:
            return 1
