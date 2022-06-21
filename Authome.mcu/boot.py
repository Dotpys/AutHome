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
from micropython import const

#==========Costants==========
WLAN_SSID = "RASPUTIN"
WLAN_PSWD = "wafer4000"
MQTT_CLIENT_ID = "AUTHOME_MCU"
MQTT_BROKER_HOSTNAME = "192.168.137.1"
MQTT_BROKER_PORT = const(1883)
MQTT_KEEPALIVE = (30)
#==========Pin assignment==========
RGB_LED_R = const(0)	# 0 RGB Led, R channel
RGB_LED_G = const(2)	# 2 RGB Led, G channel
RGB_LED_B = const(4)	# 4 RGB Led, B channel
FINGER_TX = const(13)	#13 UART TX, FINGERPRINT SENSOR RX
FINGER_RX = const(14)	#14 UART RX, FINGERPRINT SENSOR TX
RELAY_3	= const(19)		#19 Relay 3 (Demo)
RELAY_2	= const(21)		#21 Relay 2 (Demo)
RELAY_1	= const(22)		#22 Relay 1 (Demo)
RELAY_0	= const(23)		#23 Relay 0 (Lock)
PIN_DHT = const(33)		#33 DHT


#==========Global variables==========
network_interface = network.WLAN(network.STA_IF)
mqtt_client = mqtt.MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER_HOSTNAME, MQTT_BROKER_PORT, None, None, MQTT_KEEPALIVE)
#dht_sensor = dht.DHT11(machine.Pin(PIN_DHT))
led_rgb = rgbled.RGBLed(RGB_LED_R, RGB_LED_G, RGB_LED_B)
fingerprint_sensor = fingerprint.FingerprintSensor(rx=FINGER_RX, tx=FINGER_TX)
lock = relay.Lock(RELAY_0)
relay_1 = relay.Relay(RELAY_1, 1)
relay_2 = relay.Relay(RELAY_2, 1)
relay_3 = relay.Relay(RELAY_3, 1)
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

def bytes_to_guid(guid_bytes):
	'''
	Ritorna la rappresentazione sotto forma di stringa del GUID passato come argomento. 

	Formato in entrata b'\\x10\\x0E\\xBB\\xB6\\x45\\xF9\\x4C\\x09\\x9F\\x0B\\x99\\x22\\x3B\\xB7\\xAD\\x37'
	
	Formato di uscita "100EBBB645F94C099F0B99223BB7AD37"
	'''
	result = ""
	for b in  guid_bytes:
		result += f"{b:02X}"
	return result


#==========WLAN==========
def connect_network():
	if network_interface.active() == False:
		network_interface.active(True)
		#Waits for the interface to be active.
		while network_interface.active() == False:
			pass
		log("INF", "WIFI", "Initialized Wi-Fi interface")
	log("INF", "WIFI", "Trying to connect to " + WLAN_SSID)
	network_interface.connect(WLAN_SSID, WLAN_PSWD)
	#Waits for the interface to be connected to the AP.
	while network_interface.isconnected() == False:
		pass
	if_status = network_interface.ifconfig()
	subnet_mask = sum(map(lambda x:count_set_bits(int(x)), if_status[1].split(".")))
	log("INF", "WIFI", "Connected to " + WLAN_SSID)
	log("INF", "WIFI", "Device IP : " + if_status[0] + "/" + str(subnet_mask))
	log("INF", "WIFI", "Gateway   : " + if_status[2] + "/" + str(subnet_mask))
	log("INF", "WIFI", "DNS       : " + if_status[3] + "/" + str(subnet_mask))


#==========MQTT==========
def connect_to_broker():
	global mqtt_client
	log("INF", "MQTT", "Trying to connect to broker on " + MQTT_BROKER_HOSTNAME + ":" + str(MQTT_BROKER_PORT))
	mqtt_client.set_last_will("authome/mcu/status", "Offline")
	mqtt_client.connect()
	log("INF", "MQTT", "Connected to broker")
	mqtt_client.publish("authome/mcu/status", "Online")


#==========Tasks==========
def publish_sensor_data(callback_params):
	temp = esp32.raw_temperature()
	mqtt_client.publish("authome/mcu/temperature", str(temp))
	#log("INF", "ESPT", "New reading on internal temperature: " + str(temp) + "°F, sent mqtt message")
	#dht_sensor.measure()
	#temp = dht_sensor.temperature()
	#mqtt_client.publish("authome/dht/temperature", str(temp))
	#log("INF", "DHTT", "New reading on DHT temperature: " + str(temp) + "°C, sent mqtt message")
	#temp = dht_sensor.humidity()
	#mqtt_client.publish("authome/dht/humidity", str(temp))
	#log("INF", "DHTH", "New reading on DHT humidity: " + str(temp) + "%, sent mqtt message")
	pass
#TODO, forse bisogna fare una seconda lettura per poi eseguire GenModel
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
	led_rgb.set_color(rgbled.RGBLed.Magenta)
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
	led_rgb.set_color(rgbled.RGBLed.Green)

def check_finger():
	led_rgb.set_color(rgbled.RGBLed.Magenta)
	result = fingerprint_sensor.generate_image()
	if (result != 0x00):
		return
	log("INF", "FING", "Impronta rilevata, genero le caratteristiche.")
	while (True):
		result = fingerprint_sensor.image_2_tz(0x01)
		if (result == 0x00):
			break
	log("INF", "FING", "Caratteristiche generate, cerco eventuali match.")
	while (True):
		result = fingerprint_sensor.search(0x01)
		if (result[0] == 0x09):
			#Impronta non trovata
			log("INF", "FING", "Nessuna impronta corrispondente trovata.")
			led_rgb.set_color(rgbled.RGBLed.Red)
			time.sleep_ms(1500)
			return
		if (result[0] == 0x00):
			#Impronta trovata
			log("INF", "FING", "Trovata una impronta corrispondente, indice: " + str(result[1]))
			led_rgb.set_color(rgbled.RGBLed.Green)
			log("INF", "FING", "Apro la serratura per 15 secondi")
			mqtt_client.publish("authome/access", str(result[1]))
			lock.timed_unlock(0, 15000)
			break
	


def subscribe_callback(topic, msg):
	log("INF", "MQTT", "Ricevuto un messaggio sul topic " + str(topic) + " : " + str(msg))
	if (topic == b'authome/relay/1'):
		if (msg == b'0'):
			relay_1.closeNC()
		if (msg == b'1'):
			relay_1.closeNO()

	if (topic == b'authome/relay/2'):
		if (msg == b'0'):
			relay_2.closeNC()
		if (msg == b'1'):
			relay_2.closeNO()

	if (topic == b'authome/relay/3'):
		if (msg == b'0'):
			relay_3.closeNC()
		if (msg == b'1'):
			relay_3.closeNO()


#==========Main==========
def main():
	led_rgb.set_color(rgbled.RGBLed.Yellow);
	connect_network()
	connect_to_broker()
	mqtt_client.set_callback(subscribe_callback)
	mqtt_client.subscribe("authome/relay/1")
	mqtt_client.subscribe("authome/relay/2")
	mqtt_client.subscribe("authome/relay/3")
	timer_sensor_data = machine.Timer(0)
	timer_sensor_data.init(period=5*1000, callback=publish_sensor_data)
	#Normal behaviour
	led_rgb.set_color(rgbled.RGBLed.Green);
	
	#current_command = (0x01, b'\x04\x41\xED\x02\x42\x63\x4B\x51\x81\x2C\x92\x67\xE9\x1A\xE6\xDB', 0x0001)
	current_command = None
	while (True):
		#controllare il comando
		if (current_command == None):
			#check sulla presenza di una impronta per l'eventuale sblocco
			#della serratura.
			check_finger()
		if (current_command != None):
			#check id comando
			if (current_command[0] == 0x01):
				#Richiesta registrazione impronta digitale.
				log("INF", "CMND", "Richiesta la registrazione dell'utente con GUID: " + bytes_to_guid(current_command[1]) + " in posizione " + str(current_command[2]) + ".")
				register_user(current_command[1], current_command[2])
				current_command = None
			else:
				log("INF", "CMND", "Nessun comando con istruzione " + current_command[0] + " conosciuto.")
				current_command = None
		mqtt_client.check_msg()


if __name__ == "__main__":
	main()