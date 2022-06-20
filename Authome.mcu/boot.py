#==========Imports==========
import dht
import esp32
import machine
import network
import time
import umqtt.robust as mqtt
import fingerprint
import rgbled
import relay

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
TOPIC_LOCK = "authome/relay/0"
TOPIC_RELAY_1 = "authome/relay/1"
TOPIC_RELAY_2 = "authome/relay/2"
TOPIC_RELAY_3 = "authome/relay/3"
TOPIC_RELAY_4 = "authome/relay/4"
TOPIC_RELAY_5 = "authome/relay/5"
TOPIC_RELAY_6 = "authome/relay/6"
TOPIC_RELAY_7 = "authome/relay/7"
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
RELAY_5	= 15	#15 Relay 5 (Demo)
				#16 Do not use, Embedded flash
				#17 Do not use, Embedded flash
RELAY_4	= 18	#18 Relay 4 (Demo)
RELAY_3	= 19	#19 Relay 3 (Demo)
RELAY_2	= 21	#21 Relay 2 (Demo)
RELAY_1	= 22	#22 Relay 1 (Demo)
RELAY_0	= 23	#23 Relay 0 (Lock)
RELAY_6	= 25	#25 Relay 6 (Demo)
RELAY_7	= 26	#26 Relay 7 (Demo)
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
#dht_sensor = dht.DHT11(machine.Pin(PIN_DHT))
#dht_temperature = 0
#dht_humidity = 0
#Fingerprint sensor
rgb_led = rgbled.RGBLed(RGB_LED_R, RGB_LED_G, RGB_LED_B)
fingerprint_sensor = fingerprint.FingerprintSensor(rx=FINGER_RX, tx=FINGER_TX)
lock = relay.Lock(RELAY_0)
relay_1 = relay.Relay(RELAY_1, 0)
relay_2 = relay.Relay(RELAY_2, 0)
relay_3 = relay.Relay(RELAY_3, 0)
relay_4 = relay.Relay(RELAY_4, 0)
relay_5 = relay.Relay(RELAY_5, 0)
relay_6 = relay.Relay(RELAY_6, 0)
relay_7 = relay.Relay(RELAY_7, 0)
current_command = None

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

def bytes_to_guid(guid_bytes):
	'''
	Ritorna la rappresentazione sotto forma di stringa del GUID passato come argomento. 

	Formato in entrata b'\\x10\\x0E\\xBB\\xB6\\x45\\xF9\\x4C\\x09\\x9F\\x0B\\x99\\x22\\x3B\\xB7\\xAD\\x37'
	
	Formato di uscita "100EBBB6-45F9-4C09-9F0B-99223BB7AD37"
	'''
	result = ""
	for b in  guid_bytes:
		result += f"{b:02X}"
	return result


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
def publish_sensor_data(callback_params):
	temp = esp32.raw_temperature()
	mqtt_client.publish(TOPIC_MCU_TEMPERATURE, str(temp))
	#log("INF", "ESPT", "New reading on internal temperature: " + str(temp) + "°F, sent mqtt message")
	#dht_sensor.measure()
	#temp = dht_sensor.temperature()
	#mqtt_client.publish(TOPIC_DHT_TEMPERATURE, str(temp))
	#log("INF", "DHTT", "New reading on DHT temperature: " + str(temp) + "°C, sent mqtt message")
	#temp = dht_sensor.humidity()
	#mqtt_client.publish(TOPIC_DHT_HUMIDITY, str(temp))
	#log("INF", "DHTH", "New reading on DHT humidity: " + str(temp) + "%, sent mqtt message")

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


def register_user(user_id: bytes, position):
	'''
	- user_id viene fornito sotto forma di array di byte che rappresenta il GUID dell'utente nell'applicazione.
	- position viene fornito sotto forma di numero che rappresenta l'indice nella memoria del modulo
		della posizione in cui viene salvato il file di caratteristiche.
	


	1. Carica la foto dell'impronta tramite MQTT (user_id + buffer_immagine)
	2. Carica le caratteristiche dell'impronta tramite MQTT (user_id + buffer_caratteristiche)
	'''
	result = 0;
	result_data = None
	log("INF", "FING", "Registrazione utente iniziata, appoggiare l'impronta sul modulo.")
	while (True):
		result = fingerprint_sensor.generate_image();
		if (result == 0):
			break
	log("INF", "FING", "Impronta letta, carico l'immagine sul microcontrollore.")
	while (True):
		result_data = fingerprint_sensor.upload_image()
		if (result_data[0] == 0):
			break
	image_buffer = result_data[1]
	log("INF", "FING", "Caricamento completato, genero le caratteristiche dell'impronta.")
	while (True):
		result = fingerprint_sensor.image_2_tz(0x01);
		if (result == 0):
			break
	log("INF", "FING", "Caratteristiche generate, le immagazzino in memoria.")
	while (True):
		result = fingerprint_sensor.store(0x01, position)
		if (result == 0):
			break
	log("INF", "FING", "Caratteristiche immagazzinate, le carico sul microcontrollore.")
	while (True):
		result_data = fingerprint_sensor.upload_characteristic(0x01)
		if (result_data[0] == 0):
			break
	char_buffer = result_data[1]

	mqtt_client.publish(f"authome/user/{bytes_to_guid(user_id)}/image", image_buffer)
	mqtt_client.publish(f"authome/user/{bytes_to_guid(user_id)}/characteristics", char_buffer)
	mqtt_client.publish(f"authome/user/{bytes_to_guid(user_id)}/index", str(position))
	log("INF", "FING", "Registrazione di " + bytes_to_guid(user_id) + " completata.")
	
#==========Main==========
def main():
	#Initialization
	rgb_led.set_color(rgbled.RGBLed.Yellow);
	connect_network()
	connect_to_broker()
	timer_sensor_data = machine.Timer(0)
	timer_sensor_data.init(period=5*1000, callback=publish_sensor_data)
	#Normal behaviour
	rgb_led.set_color(rgbled.RGBLed.Green);
	CMND_REGISTER_FINGERPRINT = 0x01
	
	GUID_JULIEN = b'\x10\x0E\xBB\xB6\x45\xF9\x4C\x09\x9F\x0B\x99\x22\x3B\xB7\xAD\x37'
	INDEX_JULIEN = 0x0000
	current_command = (CMND_REGISTER_FINGERPRINT, GUID_JULIEN, INDEX_JULIEN)
	while (True):
		#controllare il comando
		if (current_command == None):
			#check sulla presenza di una impronta
			pass
		if (current_command != None):
			#check id comando
			if (current_command[0] == CMND_REGISTER_FINGERPRINT):
				#Richiesta registrazione impronta digitale.
				#current_command[1] é il guid dell'utente da registrare
				#current_command[2] é l'indice della memoria del modulo in cui salvare il file di caratteristiche.
				log("INF", "CMND", "Richiesta la registrazione dell'utente con GUID: " + bytes_to_guid(current_command[1]) + " in posizione " + str(current_command[2]) + ".")
				register_user(current_command[1], current_command[2])
			else:
				log("INF", "CMND", "Nessun comando con istruzione " + current_command[0] + " conosciuto.")
				current_command = None
			


if __name__ == "__main__":
	main()