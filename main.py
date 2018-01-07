from server import *
from user import *
import pickle
from sys import exit


def load_users():
    userfile = open('users.dat', 'rb')
    try:
        users = pickle.load(userfile)
    except EOFError:
        users = [Account('1377')]
    return users

def save_users():
    userfile = open('users.dat', 'wb')
    pickle.dump(accounts, userfile)

accounts = load_users()

def handle(self, conn, addr, req):
    self.log.log("Client request:", req)
    if req[1] == '':
        self.send(Response.code301('home.html'))
    else:
        self.send_file(req[1])
    # self.log.log("Client connection:", addr)
    conn.close()

print(accounts)

s = Server(True)
s.set_request_handler(handle)
s.open()
save_users()
