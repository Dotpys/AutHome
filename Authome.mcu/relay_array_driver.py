from machine import Pin

class RelayArray8:
	def __init__(self, in1, in2, in3, in4, in5, in6, in7, in8):
		__pins = []
		__pins[0] = Pin(in1, Pin.OUT, Pin.PULL_UP)
		__pins[1] = Pin(in2, Pin.OUT, Pin.PULL_UP)
		__pins[2] = Pin(in3, Pin.OUT, Pin.PULL_UP)
		__pins[3] = Pin(in4, Pin.OUT, Pin.PULL_UP)
		__pins[4] = Pin(in5, Pin.OUT, Pin.PULL_UP)
		__pins[5] = Pin(in6, Pin.OUT, Pin.PULL_UP)
		__pins[6] = Pin(in7, Pin.OUT, Pin.PULL_UP)
		__pins[7] = Pin(in8, Pin.OUT, Pin.PULL_UP)

	def boh():
		pass