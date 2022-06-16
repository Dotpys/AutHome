#==========Imports==========
import dht
import esp32
import machine
import network
import time
import umqtt.robust as mqtt
import fingerprint
import rgbled

#==========Costants==========
#Default AP information.
WLAN_SSID = "RASPUTIN"
WLAN_PSWD = "wafer4000"
#MQTT Configuration
MQTT_CLIENT_ID = "MICROCONTROLLORE"
MQTT_BROKER_HOSTNAME = "192.168.137.1"
MQTT_BROKER_PORT = 1883
MQTT_KEEPALIVE = 30
#MQTT Topics
TOPIC_BASE = "authome/"
TOPIC_MCU = TOPIC_BASE + "mcu/"
TOPIC_MCU_STATUS = TOPIC_MCU + "status"
TOPIC_MCU_TEMPERATURE = TOPIC_MCU + "temperature"
TOPIC_DHT = TOPIC_BASE + "dht/"
TOPIC_DHT_TEMPERATURE = TOPIC_DHT + "temperature"
TOPIC_DHT_HUMIDITY = TOPIC_DHT + "humidity"
#Pin assignment
RGB_LED_R = 0	# 0 RGB Led, R channel
				# 1 Do not use, REPL TX
RGB_LED_G = 2	# 2 RGB Led, G channel
				# 3 Do not use, REPL RX
RGB_LED_B = 4	# 4 RGB Led, B channel
				# 5 
				# 6 Do not use, Embedded flash
				# 7 Do not use, Embedded flash
				# 8 Do not use, Embedded flash
				# 9 Do not use, Embedded flash
				#10 Do not use, Embedded flash
				#12 Do not use, risk of bootloop
FINGER_TX = 13	#13 UART TX, FINGERPRINT SENSOR RX
FINGER_RX = 14	#14 UART RX, FINGERPRINT SENSOR TX
				#15 
				#16 Do not use, Embedded flash
				#17 Do not use, Embedded flash
				#18 
				#19 
				#21 
				#22 
				#23 
				#25 
				#26 
				#27 
				#32 
PIN_DHT = 33	#33 DHT
				#34 Input only
				#35 Input only


#==========Global variables==========
#Network objects
network_if = network.WLAN(network.STA_IF)
#MQTT objects
mqtt_client = mqtt.MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER_HOSTNAME, MQTT_BROKER_PORT, None, None, MQTT_KEEPALIVE)
#DHT objects
dht_sensor = dht.DHT11(machine.Pin(PIN_DHT))
dht_temperature = 0
dht_humidity = 0
#Fingerprint sensor
fingerprint_sensor = fingerprint.FingerprintSensor(rx=14, tx=FINGER_TX)
fingerprint_sensor_response = 0
#MCU objects
mcu_temperature = 0


#==========Utils==========
def count_set_bits(n):
	if (n==0):
		return 0
	else:
		return (n & 1) + count_set_bits(n >> 1)

def log(level, topic, message):
	#Log trough serial/UART
	print(level + " | " + topic + " | " + message)
	#Log trough MQTT
	#TODO

#==========WLAN==========
def connect_network():
	if network_if.active() == False:
		network_if.active(True)
		#Waits for the interface to be active.
		while network_if.active() == False:
			pass
		log("INF", "WIFI", "Initialized Wi-Fi interface")
	log("INF", "WIFI", "Trying to connect to " + WLAN_SSID)
	network_if.connect(WLAN_SSID, WLAN_PSWD)
	#Waits for the interface to be connected to the AP.
	while network_if.isconnected() == False:
		pass
	if_status = network_if.ifconfig()
	subnet_mask = sum(map(lambda x:count_set_bits(int(x)), if_status[1].split(".")))
	log("INF", "WIFI", "Connected to " + WLAN_SSID)
	log("INF", "WIFI", "Device IP : " + if_status[0] + "/" + str(subnet_mask))
	log("INF", "WIFI", "Gateway   : " + if_status[2] + "/" + str(subnet_mask))
	log("INF", "WIFI", "DNS       : " + if_status[3] + "/" + str(subnet_mask))

#==========MQTT==========
def connect_to_broker():
	global mqtt_client
	log("INF", "MQTT", "Trying to connect to broker on " + MQTT_BROKER_HOSTNAME + ":" + str(MQTT_BROKER_PORT))
	mqtt_client.set_last_will(TOPIC_MCU_STATUS, "Offline")
	mqtt_client.connect()
	log("INF", "MQTT", "Connected to broker")
	mqtt_client.publish(TOPIC_MCU_STATUS, "Online")


#==========Tasks==========
def ping(callback_params):
	temp = esp32.raw_temperature()
	mqtt_client.publish(TOPIC_MCU_TEMPERATURE, str(temp))

def check_sensor_data(callback_params):
	"""
	Effettua una lettura di tutti i sensori del sistema, manda messaggi di aggionrnamento dei valori al broker solo se necessario.
	"""
	global dht_temperature, dht_humidity, mcu_temperature
	
	#Internal ESP32 temperature sensor [F]
	temp = esp32.raw_temperature()
	if temp != mcu_temperature:
		mcu_temperature = temp
		mqtt_client.publish(TOPIC_MCU_TEMPERATURE, str(mcu_temperature))
		log("INF", "ESPM", "New reading on internal temperature: " + str(mcu_temperature) + "°F, sent mqtt message")
	
	#DHT temperature & humidity sensor [C]
	#dht_sensor.measure()
	#temp = dht_sensor.temperature()
	if temp != dht_temperature:
		#dht_temperature = temp
		mqtt_client.publish(TOPIC_DHT_TEMPERATURE, str(dht_temperature))
		#log("INF", "DHTT", "New reading on DHT temperature: " + str(dht_temperature) + "°C, sent mqtt message")
	#DHT temperature sensor [C]
	#temp = dht_sensor.humidity()
	if temp != dht_humidity:
		#dht_humidity = temp
		mqtt_client.publish(TOPIC_DHT_HUMIDITY, str(dht_humidity))
		#log("INF", "DHTH", "New reading on DHT humidity: " + str(dht_humidity) + "%, sent mqtt message")

def finger_check():
	result: int = 0
	log("INF", "FING", "Appoggia il dito")
	while (True):
		result = fingerprint_sensor.generate_image()
		if (result == 0):
			break
	log("INF", "FING", "Impronta riconosciuta, provo a scaricarla...")
	dat = fingerprint_sensor.upload_image()
	mqtt_client.publish("authome/fingerprint/data", dat[1])

def check_connection(c):
	if network_if.active() == False:
		print("Network interface disactivated")
	if network_if.isconnected() == False:
		print("Disconnected from network")
	

#==========Main==========
def main():
	r = machine.Pin(RGB_LED_R, machine.Pin.OUT, machine.Pin.PULL_DOWN)
	g = machine.Pin(RGB_LED_G, machine.Pin.OUT, machine.Pin.PULL_DOWN)
	b = machine.Pin(RGB_LED_B, machine.Pin.OUT, machine.Pin.PULL_DOWN)
	
	a = rgbled.RGBLed(r, g, b)
	a.set_color(rgbled.RGBLed.Green)
	time.sleep_ms(500)
	a.set_color(rgbled.RGBLed.Red)
	time.sleep_ms(500)
	a.set_color(rgbled.RGBLed.Cyan)
	time.sleep_ms(500)
	a.set_color(rgbled.RGBLed.Black)
	time.sleep_ms(500)
	a.set_color(rgbled.RGBLed.White)

	connect_network()
	connect_to_broker()
	timer_mcu_temp = machine.Timer(0)
	timer_mcu_temp.init(period=5*1000, callback=ping)
	#timer_sensor_check = machine.Timer(1)
	#timer_sensor_check.init(period=1000, callback=check_sensor_data)
	while (True):
		finger_check()


if __name__ == "__main__":
	main()