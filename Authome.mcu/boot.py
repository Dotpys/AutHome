#==========Imports==========
import network
import umqtt

#==========Costants==========
#Default AP information.
WLAN_SSID = "GHST"
WLAN_PSWD = "wafer4000"

#==========Globals==========
#HAL objects.
sta_if = network.WLAN(network.STA_IF)
#MQTT objects
mqtt_client = umqtt.MQTTClient("mqtt-explorer-a95044b7", "192.168.50.7", 1883, None, None, 5)

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
	log("INF", "MQTT", "Trying to connect to broker...")
	mqtt_client.connect()
	log("INF", "MQTT", "Connected to broker")

#==========Main==========
def main():
	check_if()
	connect_to_ap(WLAN_SSID, WLAN_PSWD)
	connect_to_broker()

if __name__ == "__main__":
	main()