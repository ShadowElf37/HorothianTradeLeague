def nall(*args):
    return all(args) or (not all(args))

def client_error_msg(msg):
    return '<html>' + msg + '<br><a href="home.html">Go back.</a></html>'

def td_wrap(s):
    return '\n<td>' + s + '</td>'