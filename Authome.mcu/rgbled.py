import machine

class RGBLed:

	Black	= (0, 0, 0)
	Red		= (1, 0, 0)
	Green	= (0, 1, 0)
	Blue	= (0, 0, 1)
	Yellow	= (1, 1, 0)
	Cyan	= (0, 1, 1)
	Magenta	= (1, 0, 1)
	White	= (1, 1, 1)

	r = None
	g = None
	b = None

	def __init__(self, r, g, b):
		self.r = machine.Pin(r, machine.Pin.OUT, machine.Pin.PULL_DOWN)
		self.g = machine.Pin(g, machine.Pin.OUT, machine.Pin.PULL_DOWN)
		self.b = machine.Pin(b, machine.Pin.OUT, machine.Pin.PULL_DOWN)

	def set_color(self, color):
		self.r.value(1-color[0])
		self.g.value(1-color[1])
		self.b.value(1-color[2])