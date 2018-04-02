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

class Console:
	def __init__(self):
		self.functions = {'echo':self.echo, 'login':self.login}
		self.state = {'logged_in':False}
		self.user_admin = 'admin'
		self.pass_admin = 'secretpassword'
		self.color = WHITE

	def call(self, name, args):
		try:
			output = self.functions[name](*args)
			col = self.color.cpl()
			self.color = WHITE
			return col + output
		except KeyError:
			return RED.cpl() + 'Unknown command \'' + name + '\'. Type \'help\' for a list of available commands.'
		except IndexError:
			return RED.cpl() + 'Invalid parameters for command \'' + name + '\'.'


	def echo(self, *args):
		return ' '.join(args)

	def login(self, *args):
		if args[0] == self.user_admin and args[1] == self.pass_admin:
			self.color = GREEN
			return 'Successfully logged in. Welcome commander.'
		else:
			self.color = RED
			return 'Invalid credentials.'
