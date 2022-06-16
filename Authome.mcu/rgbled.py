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
		self.r = r
		self.g = g
		self.b = b

	def set_color(self, color):
		self.r.value(1-color[0])
		self.g.value(1-color[1])
		self.b.value(1-color[2])