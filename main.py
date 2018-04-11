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
import console
import random
import datetime
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
hunts = [h for a in accounts for h in a.my_hunts]
sales = [s for a in accounts for s in a.my_sales]
lib.bootstrapper.accounts = accounts  # Not sure why this is necessary, but the funcs in there can't handle main's vars
lib.bootstrapper.groups = groups
lib.bootstrapper.hunts = hunts
lib.bootstrapper.sales = sales
lib.bootstrapper.pm_group = groups[0]
lib.bootstrapper.log_transactions = log_transactions
lib.bootstrapper.log_signin = log_signin
lib.bootstrapper.log_signup = log_signup
lib.bootstrapper.whitelist = whitelist
lib.bootstrapper.host = host
lib.bootstrapper.port = port
pm_group = groups[0]
error = ''
consoles = dict()
CB = get_account_by_id('1377')

import handler  # Again, I don't know why, but it just cannot handle being put before all the bootstrapper init


# ---------------------------------


def handle(self, conn, addr, request):
    global error
    while self.paused.get(addr[0], False):
        time.sleep(0.001)
    self.pause(addr[0])
    Thread(target=self.unpause, args=(addr[0],)).start()

    # Log request
    if log_request or request.file_type in ('html', 'htm', 'act'):
        self.log.log("Request from ", addr[0], ":", [request.method, request.address, request.cookies] + ([request.flags,] if log_request_flags else []) + [request.post_values,])

    # Finds the client by cookie, creates a response to modify later
    response = Response()
    client = get_account_by_id(request.get_cookie('client-id'))
    request.client = client
    client.ip_addresses.add(addr[0])
    response.logged_in = not client.shell

    # Default render values - these are input automatically to renders
    global host, port
    render_defaults = {'error':error, 'number_of_messages':len(list(filter(lambda x: not x.read, client.messages))), 'host':publichost, 'port':port, 'username':client.username, 'id':client.id, 'hunt_total':client.total_hunts, 'hunt_count':client.active_hunts, 'balance':client.balance}
    response.default_renderopts = render_defaults

    # Make sure client has a cookie
    if client.id is None:
        response.add_cookie('client-id', 'none', 'path=/')
    # Make sure SID is valid
    elif request.get_cookie('validator') != client.validator and response.logged_in and require_validator:
        response.add_cookie('client-id', 'none', 'path=/')
        response.add_cookie('validator', 'none', 'path=/')
        response.logged_in = False
        error = self.throwError(5, 'a', '/home/login.html', conn, response=response)
        self.log.log(addr[0], '- Client\'s cookies don\'t match.', lvl=Log.ERROR)
        return
    # Record activity
    elif response.logged_in:
        client.last_activity = time.strftime('%X (%x)')

    # Pull simpler address from request
    address = '/'.join(request.address).split('-')[0]

    # If the post values are magically empty, that's a problem... happens more than you'd think
    if request.method == "POST" and not request.post_values:
        error = self.throwError(0, 'a', request.get_last_page(), conn, response=response)
        self.log.log(addr[0], '- That thing happened again... sigh.', lvl=Log.ERROR)
        return

    # Generate handler
    request_handler = handler.INDEX.get(address, handler.DefaultHandler)(self, conn, addr, request, response)
    # Get output
    response = request_handler.call()

    # Error
    if response is None:
        error = request_handler.response.error
        return

    # Adds an error, sets page cookie (that thing that lets you go back if error), and sends the response off
    error = ''
    if request.address[-1].split('.')[-1] in ('html', 'htm'):
        response.add_cookie('page', '/'.join(request.address))

    self.send(response, conn)
    conn.close()


# TURN DEBUG OFF FOR ALL REAL-WORLD TRIALS OR ANY ERROR WILL CAUSE A CRASH
# USE SHUTDOWN URLs TO TURN OFF

#host = '192.168.1.180'
host = '0.0.0.0'
publichost = 'projectmercury.asuscomm.com'
port = 80
s = Server(host=host, port=port, debug=True, include_debug_level=False)
s.log.log('Accounts:', accounts, lvl=Log.INFO)
s.log.log('Groups:', groups, lvl=Log.INFO)
s.set_request_handler(handle)
s.open()
save_users()
lib.bootstrapper.running = False
