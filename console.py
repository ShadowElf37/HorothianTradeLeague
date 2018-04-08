# ADMIN LOGIN: admin/secretpassword
# USER LOGIN: mercury/6865726d6573

class Format:
    bold = 'b'
    underline = 'u'
    italic = 'i'
    def __init__(self, color='#fff', *styles):
        self.styles = styles
        self.color = color

    def cpl(self):
        return ''.join(self.styles)+'c'+'|'+self.color+'|'

    def set_styles(self, *args):
        self.styles = args
        return self

RED = Format('#f00')
YELLOW = Format('#ff0')
GREEN = Format('#0f0')
TEAL = Format('#0ff')
BLUE = Format('#00f')
PURPLE = Format('#f0f')
WHITE = Format('#fff')


class File:
    def __init__(self, name, text='', readable=True):
        self.name = name
        self.text = text
        self.size = len(text)
        self.readable = readable

    def read(self):
        if self.readable:
            return self.text+'\n[EOF]'
        else:
            return 0

class Console:
    state = {'mercury1':False}

    def __init__(self, account_list):
        self.accounts = account_list
        self.functions_normal = {
            'echo':self.echo,
            'login':self.login,
            'help':self.help_normal,
        }
        self.functions_special = {
            'ls':self.list,
            'echo':self.echo,
            'help':self.help_special,
            'cat':self.cat,
            'sizeof':self.size,
            'status':self.status,
            'mercury-unlock':self.unlock,
        }
        self.functions_full = dict(list(self.functions_special.items()) + list({
           'unlock':self.feature_unlock,
           'help':self.help_full,
           'hermes':self.hermes
        }.items()))
        self.functions_admin = {
            'shutdown':self.shutdown,
            'help':self.help_admin,
            'hermes':self.hermes,
            'cmdwrite':self.write_cmd,
            'cmdclear':self.clear_cmd,
            'whitelist':self.whitelist,
            'force':self.forcepay
        }
        self.state = {'logged_in_admin':False, 'logged_in_special':False}
        self.default_format = TEAL
        self.format = self.default_format

        self.user_admin = 'admin'
        self.pass_admin = 'secretpassword'
        self.user = 'mercury'
        self.pwd = '6865726d6573'  # hermes

        self.files = [
            File('data.txt', open('data/console_files/data.txt').read()),
            File('version.txt', open('VERSION').read()),
            File('account_viewer.exe', '0'*1633, readable=False),
            File('server_launcher.exe', '0'*10301, readable=False),
            File('mercury.pyc', open('data/console_files/mercury.txt').read()),
            File('messages1.txt', open('data/console_files/messages1.txt').read()),
        ]

    def call(self, name, args):
        try:
            output = (self.functions_full if Console.state['mercury1'] and self.state['logged_in_special'] else self.functions_special if self.state['logged_in_special'] else self.functions_admin if self.state['logged_in_admin'] else self.functions_normal)[name](*args)
            fmt = self.format.cpl()
            self.format = self.default_format
            return fmt + output.strip()
        except KeyError:
            return RED.cpl() + 'Unknown command \'' + name + '\'. Type \'help\' for a list of available commands.'
        except IndexError:
            return RED.cpl() + 'Invalid parameters for command \'' + name + '\'.'


    # COMMANDS
    def help_admin(self, *args):
        return '''
                help - list available commands
                shutdown - shuts the server down
                whitelist <fname> <lname> - lists names or adds to the whitelist
                hermes <attr> - get any attribute of an account
                cmdwrite <python> - writes a line of code to cmd.py for execution
                cmdclear - writes blank string to cmd.py
                force <id> <id> <amount> - forces an amount of money from one account to the other regardless of balance
        '''
    def help_special(self, *args):
        return '''help - list available commands
                  echo <args> - print a message
                  ls - list system files in working directory
                  sizeof <file> - give size of file
                  cat <file> - read a file's contents
                  status <server> - gives system status
                  '''
    def help_full(self, *args):
        return self.help_special() + '''unlock <feature> - unlocks a locked Project feature
        '''
    def help_normal(self, *args):
        return	''' help - list available commands
                    echo <args> - print a message
                    login <user> <pass> - grants access to MERCURY
                '''

    def echo(self, *args):
        return ' '.join(args)

    def status(self, *args):
        self.format = GREEN
        if not args or not args[0] or args[0] == 'mercury':
            f = open('conf/progress.cfg', 'r').read()
            market = False
            hs = False
            for line in f.split('\n'):
                if line.split(':')[0] == 'Market' and '1/2' not in line:
                    market = True
                elif line.split(':')[0] == 'Hunt Submission' and '1/2' not in line:
                    hs = True
            return '\n'.join(['Collection status: interrupted.',
                              'data.txt size: 111 Bytes',
                              'Submission status: '+('standing by...' if not hs else 'ready.'),
                              'Market status: '+('standing by...' if not market else 'ready.')])
        elif args[0] == 'hermes':
            return '\n'.join(['REQUEST FROM FOREIGN SERVER ACKNOWLEDGED',
                              'Collection status: 497 records.',
                              'Time to HERMES db write: 253 records.',
                              'Authorized types: us,pw,cl,ms.',
                              'ACK: OK. ER. OK. OK.'])

    def login(self, *args):
        if args[0] == self.user_admin and args[1] == self.pass_admin:
            self.format = GREEN
            self.state['logged_in_admin'] = True
            return 'Successfully logged in. Welcome commander.'
        elif args[0] == self.user and args[1] == self.pwd:
            self.format = GREEN
            self.state['logged_in_special'] = True
            return 'Transfer to server MERCURY successful.\n' + self.status()
        else:
            self.format = RED
            return 'Invalid credentials.'

    def list(self, *args):
        return '\n'.join([f.name for f in self.files])

    def cat(self, *args):
        f = args[0]
        for fl in self.files:
            if fl.name == f:
                if fl.read():
                    return fl.read()
                else:
                    self.format = RED
                    return 'Unable to read file.'
        self.format = RED
        return 'File not found.'

    def unlock(self, *args):
        if args[0] == 'americankhanate':
            Console.state['mercury1'] = True
            self.files += [
                File('messages2.txt', open('data/console_files/messages2.txt').read())
            ]
            self.format = GREEN
            return 'Server state changed. Additional commands unlocked.'

    def size(self, *args):
        for fl in self.files:
            if fl.name == args[0]:
                return str(len(fl.read())) + ' Bytes'
        self.format = RED
        return 'File not found.'

    def feature_unlock(self, *args):
        f = open('conf/progress.cfg', 'r').read()
        fw = open('conf/progress.cfg', 'w')
        total = []
        for line in f.split('\n'):
            if line.split(':')[0].lower() == args[0]:
                total.append(line.replace('1/2', '1'))
            else:
                total.append(line)
        total = '\n'.join(total)
        fw.write(total)
        fw.close()
        return args[0].title() + ' unlocked. Recommend check progress.html to confirm.'

    def hermes(self, *args):
        l = ['\t'*21 + 'User | '+args[0], '-'*50]
        name = lambda u: ('%25s' % u.get_name())
        if args[0] == 'username':
            for user in self.accounts:
                l.append(name(user) + ' | ' + user.username)
        elif args[0] == 'password':
            for user in self.accounts:
                l.append(name(user) + ' | ' + '[ERROR]')
        elif args[0] == 'coalition':
            for user in self.accounts:
                l.append(name(user) + ' | ' + user.coalition.name)
        elif args[0] == 'messages':
            for user in self.accounts:
                l.append(name(user) + ' | ' + str(len(user.messages)))
        elif self.state['logged_in_admin']:
            attributes = args[0].split('.')
            e = [u for u in self.accounts]
            for a in attributes:
                for i in range(len(e)):
                    try:
                        e[i] = getattr(e[i], a)
                    except AttributeError:
                        raise IndexError
            try:
                for i in range(len(self.accounts)):
                    l.append(name(self.accounts[i]) + ' | ' + str(e[i]))
            except AttributeError:
                raise IndexError
        else:
            raise IndexError
        return 'REQUEST FROM FOREIGN SERVER ACKNOWLEDGED\n'+'\n'.join(l)

    def write_cmd(self, *args):
        open('cmd.py', 'w').write(' '.join(args))
        return 'Write successful.'

    def clear_cmd(self, *args):
        open('cmd.py', 'w').write('')
        return 'Write successful.'

    def whitelist(self, *args):
        f = open('conf/whitelist.cfg', 'r').read()
        fw = open('conf/whitelist.cfg', 'w')
        if not args or args[0] == '':
            fw.write(f)
            return f
        else:
            fw.write(f+'\n'+' '.join(args[:2]))
        return 'Write successful.'

    def forcepay(self, *args):
        id1, id2, amt = args
        a1 = [a for a in self.accounts if a.id == id1][0]
        a2 = [a for a in self.accounts if a.id == id2][0]
        amt = float(amt)
        a1.balance -= amt
        a2.balance += amt
        return 'Forced transaction. %s: %s > %s, %s: %s > %s' % (id1, str(a1.balance+amt), str(a1.balance), id2, str(a2.balance-amt), str(a2.balance))

    def shutdown(self, *args):
        return 'Not yet.'


# 6865726d6573