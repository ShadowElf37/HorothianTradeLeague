from server import *
import pickle
from sys import exit

s = Server()

def handle(self, conn, addr, req):
    self.log.log("Client request:", req)
    if req[1] == '':
        self.send(Response.code301('home.html'))
    else:
        self.send_file(req[1])
    # self.log.log("Client connection:", addr)
    conn.close()
s.set_request_handler(handle)

s.open()
