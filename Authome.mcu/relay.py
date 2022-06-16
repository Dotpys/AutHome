from machine import Pin
from time import sleep

RELAY_ON = True
RELAY_OFF = False

class Relay:
	"""
	"""

	__slots__ = ("__state", "__relay")

	def __init__(self, id):
		self.__state = RELAY_OFF
		self.__relay = Pin(
			id,
			mode=Pin.OUT,
			pull=Pin.PULL_DOWN,
			value=self.__state)


	def on():
		__relay.on()
	

	def off():
		__relay.off()


	def toggle(self):
		self.__state = not self.__state
		self.__relay.value(self.__state)
	

	def openNC():
		pass


	def closeNC():
		pass


	def openNO():
		pass


	def closeNO():
		pass

a = Relay(12)
while (True):
	a.toggle()
	sleep(1)