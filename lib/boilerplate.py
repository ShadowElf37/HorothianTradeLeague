def nall(*args):
    return all(args) or (not all(args))

def client_error_msg(msg):
    return '<html>' + msg + '<br><a href="home.html">Go back.</a></html>'

def td_wrap(s):
    return '\n<td>' + s + '</td>'

# Replaces all %21 to ! etc.
def post_to_html_escape(d):
    i = d.find('%')
    while True:
        i = d.find('%')
        code = d[i + 1:i + 3]
        if i == -1:
            break
        d = d.replace('%' + code, '&#x{};'.format(code))
    return d

def cap(v, l):
    if v > l:
        return l
    return v
def ground(v, l):
    if v < l:
        return l
    return v