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
		self.functions = {'echo':echo}

	def call(self, name, args):
		try:
			return WHITE.cpl() + self.functions[name](*args)
		except KeyError:
			return YELLOW.cpl() + 'Unknown command \'' + name + '\'. Type \'help\' for a list of available commands.'
		except IndexError:
			return YELLOW.cpl() + 'Invalid parameters for command \'' + name + '\'.'


def echo(*args):
	return ' '.join(args)