import machine
from machine import Pin
import time

trig = Pin(13, Pin.OUT)
echo = Pin(34, Pin.IN)

high = False
startTime = 0
stopTime = 0

def on_change(p):
	global startTime, stopTime
	print("Fall")
	stopTime = time.ticks_us()
	diff = time.ticks_diff(stopTime, startTime)
	print(str(diff / 58) + " cm")


echo.irq(handler=on_change, trigger=Pin.IRQ_RISING)

def trigger():
	global trig, startTime, stopTime
	trig.on()
	startTime = time.ticks_us()
	time.sleep_us(10)
	trig.off()

trigger()