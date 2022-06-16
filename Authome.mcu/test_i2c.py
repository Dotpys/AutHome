from machine import I2C
from bme280 import *
from utime import sleep
i2c = I2C(0, scl=Pin(26), sda=Pin(27), freq=5000)
bme280 = BME280(i2c=i2c)
while True:
    print(bme280.values)
    sleep(1)