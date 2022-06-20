import machine
import time

class Relay:

	__state = 0
	__relay = None

	def __init__(self, id, value):
		self.__state = value
		self.__relay = machine.Pin(
			id,
			mode = machine.Pin.OUT,
			pull = machine.Pin.PULL_DOWN,
			value = self.__state)


	def on():
		__relay.on()
	

	def off():
		__relay.off()


	def state():
		return __state;


	def toggle(self):
		self.__state = not self.__state
		self.__relay.value(self.__state)
	

	def openNC(self):
		self.__state = 0
		self.__relay.value(self.__state)


	def closeNC(self):
		self.__state = 1
		self.__relay.value(self.__state)


	def openNO(self):
		self.__state = 1
		self.__relay.value(self.__state)


	def closeNO(self):
		self.__state = 0
		self.__relay.value(self.__state)

class Lock(Relay):
	
	__relay = None
	
	def __init__(self, pin):
		super().__init__(pin, 1)
	
	def timed_unlock(self, millis_before, millis):
		'''Waits millis_before milliseconds, opens the lock for millis milliseconds, then closes the lock.'''
		time.sleep_ms(millis_before)
		self.closeNO()
		time.sleep_ms(millis)
		self.openNO()