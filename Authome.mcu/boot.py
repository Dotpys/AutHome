#==========Imports==========
import dht
import esp32
import machine
import network
import time
import umqtt
from drivers.fingerprint import FingerprintSensor

#==========Costants==========
#Default AP information.
WLAN_SSID = "GHST"
WLAN_PSWD = "wafer4000"
#MQTT Configuration
MQTT_CLIENT_ID = "esp32-endpoint"
MQTT_BROKER_HOSTNAME = "192.168.34.7"
MQTT_BROKER_PORT = 1883
#MQTT Topics
TOPIC_BASE = "authome/"
TOPIC_MCU = TOPIC_BASE + "mcu/"
TOPIC_MCU_STATUS = TOPIC_MCU + "status"
TOPIC_MCU_TEMPERATURE = TOPIC_MCU + "temperature"
TOPIC_DHT = TOPIC_BASE + "dht/"
TOPIC_DHT_TEMPERATURE = TOPIC_DHT + "temperature"
TOPIC_DHT_HUMIDITY = TOPIC_DHT + "humidity"
#DHT Pin number
PIN_DHT = 33


#==========Globals==========
#WLAN objects
sta_if = network.WLAN(network.STA_IF)
#MQTT objects
mqtt_client = umqtt.MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER_HOSTNAME, MQTT_BROKER_PORT, None, None, 5)
#DHT objects
dht_sensor = dht.DHT11(machine.Pin(PIN_DHT))


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
def check_if():
	if sta_if.active() == False:
		sta_if.active(True)
		#Waits for the interface to be active.
		while sta_if.active() == False:
			pass
		log("INF", "WIFI", "Initialized Wi-Fi interface")


def connect_to_ap(ssid, password):
	log("INF", "WIFI", "Trying to connect to " + WLAN_SSID)
	sta_if.connect(WLAN_SSID, WLAN_PSWD)
	#Waits for the interface to be connected to the AP.
	while sta_if.isconnected() == False:
		pass
	log_if_status()


def log_if_status():
	if_status = sta_if.ifconfig()
	subnet_mask = sum(map(lambda x:count_set_bits(int(x)), if_status[1].split(".")))
	log("INF", "WIFI", "Connected to " + WLAN_SSID)
	log("INF", "WIFI", "    Device IP : " + if_status[0] + "/" + str(subnet_mask))
	log("INF", "WIFI", "    Gateway   : " + if_status[2] + "/" + str(subnet_mask))
	log("INF", "WIFI", "    DNS       : " + if_status[3] + "/" + str(subnet_mask))

#==========MQTT==========
def connect_to_broker():
	global mqtt_client
	log("INF", "MQTT", "Trying to connect to broker on " + MQTT_BROKER_HOSTNAME + ":" + str(MQTT_BROKER_PORT))
	mqtt_client.set_last_will(TOPIC_MCU_STATUS, "Offline")
	mqtt_client.connect()
	log("INF", "MQTT", "Connected to broker")
	mqtt_client.publish(TOPIC_MCU_STATUS, "Online")

#==========Main==========
def main():
	check_if()
	connect_to_ap(WLAN_SSID, WLAN_PSWD)
	connect_to_broker()
	fs = FingerprintSensor(rx=14, tx=12)
	log("INF", "FING", "Sensore di imprtonta inizializzato")
	result: int = 0
	log("INF", "FING", "Appoggia il dito")
	while (True):
		result = fs.generate_image()
		if (result == 0):
			break
	log("INF", "FING", "Impronta riconosciuta, provo a scaricarla...")
	dat = fs.upload_image()
	#while (True):
	#	mcu_temp = esp32.raw_temperature()
	#	mqtt_client.publish(TOPIC_MCU_TEMPERATURE, str(int(mcu_temp)))
	#	dht_sensor.measure()
	#	mqtt_client.publish(TOPIC_DHT_TEMPERATURE, str(dht_sensor.temperature()))
	#	mqtt_client.publish(TOPIC_DHT_HUMIDITY, str(dht_sensor.humidity()))
	#	time.sleep_ms(1000)


if __name__ == "__main__":
	main()