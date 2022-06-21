import machine
from micropython import const
import time

__ACK_OK = const(0x00)

__OPCODE_GENIMG = const(0x01)
__OPCODE_IMG2TZ = const(0x02)
__OPCODE_MATCH = const(0x03)
__OPCODE_SEARCH = const(0x04)
__OPCODE_REGMODEL = const(0x05)
__OPCODE_STORE = const(0x06)
__OPCODE_LOADCHAR = const(0x07)
__OPCODE_UPCHAR = const(0x08)
__OPCODE_DOWNCHAR = const(0x09)
__OPCODE_UPIMAGE = const(0x0A)
__OPCODE_READSYSPARA = const(0x0F)

__PACKET_ID_COMMAND = const(0x01)
__PACKET_ID_ENDDATA = const(0x08)

__PACKET_HEADER = b'\xEF\x01'

class FingerprintSensor:
	"""
	Class used to interface with a fingerprint
	sensor trough serial communication.
	"""

	__address = 0xFFFFFFFF
	#__password = 0x00000000
	__lib_size = 150
	__packet_size = 128

	__packet_head_buffer = bytearray(9)
	__packet_body_buffer = None


	__image_buffer = bytearray(0x9000)
	__char_buffer = bytearray(0x600)


	def __init__(self, tx: int, rx: int) -> None:
		self.__channel = machine.UART(2)
		self.__channel.init(
			baudrate=57600,
			bits=8,
			parity=None,
			stop=1,
			tx=tx,
			rx=rx,
			timeout=1000,
			timeout_char=1000)
		time.sleep_ms(500)
		result = self.read_system_parameters()
		if (result[0] == __ACK_OK):
			self.__lib_size = int.from_bytes(result[1][4:6], 'big')
			self.__packet_size = 2**(5 + int.from_bytes(result[1][12:14], 'big'))
		self.__packet_body_buffer = bytearray(self.__packet_size)


	#Instruction 0x01
	def generate_image(self):
		instruction_packet = self.__generate_packet(__PACKET_ID_COMMAND, [__OPCODE_GENIMG])
		writtenBytes = self.__channel.write(instruction_packet)
		response_packet = self.__channel.read(12)
		#TODO: Add logging
		return response_packet[9]


	#Instruction 0x02
	def image_2_tz(self, buffer_id: int) -> int:
		if (buffer_id != 0x01):
			buffer_id = 0x02
		instruction_packet = self.__generate_packet(__PACKET_ID_COMMAND, [__OPCODE_IMG2TZ, buffer_id])
		self.__channel.write(instruction_packet)
		response_packet = self.__channel.read(12)
		return response_packet[9]


	#Instruction 0x03
	def match(self) -> tuple[int, int]:
		instruction_packet = self.__generate_packet(__PACKET_ID_COMMAND,[__OPCODE_MATCH])
		self.__channel.write(instruction_packet)
		response_packet = self.__channel.read(14)
		response_ack = response_packet[9]
		if (response_ack == __ACK_OK):
			return (response_ack, int.from_bytes(response_packet[10:2], 'big')) #slice fatto male?
		else:
			return (response_ack, [])


	#Instruction 0x04
	def search(self, buffer_id: int) -> tuple[int, int]:
		if(buffer_id != 0x01):
			buffer_id = 0X02
		content = [__OPCODE_SEARCH, buffer_id]
		content.append(0x00)
		content.append(0x00)
		content.append((self.__lib_size & 0xFF00) >> 8)
		content.append((self.__lib_size & 0x00FF) >> 0)
		instruction_packet = self.__generate_packet(__PACKET_ID_COMMAND, content)
		self.__channel.write(instruction_packet)
		response_packet = self.__channel.read(16)
		response_ack = response_packet[9]
		if(response_ack == __ACK_OK):
			return (response_ack, int.from_bytes(response_packet[10:12], 'big'))
		else:
			return (response_ack, [])


	#Instruction 0x06
	def store(self, buffer_id: int, page_id) -> int:
		if(buffer_id != 0x01):
			buffer_id = 0X02
		content = [__OPCODE_STORE, buffer_id]
		content.append((page_id & 0xFF00) >> 8)
		content.append((page_id & 0x00FF) >> 0)
		instruction_packet = self.__generate_packet(__PACKET_ID_COMMAND, content)
		self.__channel.write(instruction_packet)
		response_packet = self.__channel.read(12)
		return response_packet[9]


	#Instruction 0x08
	def upload_characteristic(self, buffer_id: int) -> tuple[int, bytes]:
		"""
		Il modulo invia i dati dell'immagine dal buffer di immagini sulla linea seriale.
		"""
		#Genera il pacchetto di istruzioni e lo invia
		if(buffer_id != 0x01):
			buffer_id = 0X02
		content = [__OPCODE_UPCHAR, buffer_id]
		instruction_packet = self.__generate_packet(__PACKET_ID_COMMAND, content)
		self.__channel.write(instruction_packet)
		#Riceve il pacchetto di risposta.
		response_packet = self.__channel.read(12)
		response_ack = response_packet[9]
		if (response_ack == __ACK_OK):
			#Codice di risposta corretto, il modulo invia altri pacchetti.
			progress = 0
			end: bool = False
			while (not end):
				#Legge l'intestazione del pacchetto.
				self.__channel.readinto(self.__packet_head_buffer, 9)
				#Estrae e controlla il codice del pacchetto, se risulta uguale ad __PACKET_ID_ENDDATA significa che é questo
				#é l'ultimo pacchetto che il modulo invierá.
				packet_id = int.from_bytes(self.__packet_head_buffer[6:7], 'big')
				if (packet_id == __PACKET_ID_ENDDATA):
					end = True
				#Legge il contenuto del pacchetto.
				self.__channel.readinto(self.__packet_body_buffer, self.__packet_size)
				if (buffer_id == 0x01):
					self.__char_buffer[progress:(progress+self.__packet_size)] = self.__packet_body_buffer[0:self.__packet_size]
				if (buffer_id == 0x02):
					self.__char_buffer_2[progress:(progress+self.__packet_size)] = self.__packet_body_buffer[0:self.__packet_size]
				progress+=self.__packet_size
				#Legge i due byte di checksum.
				self.__channel.read(2)
			if (buffer_id == 0x01):
				return (response_ack, self.__char_buffer)
			if (buffer_id == 0x02):
				return (response_ack, self.__char_buffer)
		else:
			return (response_ack, [])


	#Instruction 0x0A
	def upload_image(self) -> tuple[int, bytes]:
		"""
		Il modulo invia i dati dell'immagine dal buffer di immagini sulla linea seriale.
		"""
		#Genera il pacchetto di istruzioni e lo invia
		instruction_packet = self.__generate_packet(__PACKET_ID_COMMAND, [__OPCODE_UPIMAGE])
		self.__channel.write(instruction_packet)
		#Riceve il pacchetto di risposta.
		response_packet = self.__channel.read(12)
		response_ack = response_packet[9]
		if (response_ack == __ACK_OK):
			#Codice di risposta corretto, il modulo invia altri pacchetti.
			progress = 0
			end: bool = False
			while (not end):
				#Legge l'intestazione del pacchetto.
				self.__channel.readinto(self.__packet_head_buffer, 9)
				#Estrae e controlla il codice del pacchetto, se risulta uguale ad __PACKET_ID_ENDDATA significa che é questo
				#é l'ultimo pacchetto che il modulo invierá.
				packet_id = int.from_bytes(self.__packet_head_buffer[6:7], 'big')
				if (packet_id == __PACKET_ID_ENDDATA):
					end = True
				#Legge il contenuto del pacchetto.
				self.__channel.readinto(self.__packet_body_buffer, self.__packet_size)
				self.__image_buffer[progress:(progress+self.__packet_size)] = self.__packet_body_buffer[0:self.__packet_size]
				progress+=self.__packet_size
				#Legge i due byte di checksum.
				self.__channel.read(2)
			return (response_ack, self.__image_buffer)
		else:
			return (response_ack, [])


	#Instruction 0x0F
	def read_system_parameters(self) -> tuple[int, bytes]:
		#Genera il pacchetto di istruzione e lo invia.
		instruction_packet = self.__generate_packet(__PACKET_ID_COMMAND, [__OPCODE_READSYSPARA])
		self.__channel.write(instruction_packet)
		#Legge il contenuto del pacchetto.
		response_packet = self.__channel.read(28)
		response_ack = response_packet[9]
		if (response_ack == __ACK_OK):
			return (response_ack, response_packet[10:26])
		else:
			return (response_ack, [])


	def __generate_packet(self, packet_id, content):
		result = bytearray(__PACKET_HEADER)
		result.append((self.__address & 0xFF000000) >> 24)
		result.append((self.__address & 0x00FF0000) >> 16)
		result.append((self.__address & 0x0000FF00) >>  8)
		result.append((self.__address & 0x000000FF) >>  0)
		result.append(packet_id)
		checksum = packet_id
		length = len(content) + 2
		result.append((length & 0x0000FF00) >> 8)
		result.append((length & 0x000000FF) >> 0)
		checksum += result[-2]
		checksum += result[-1]
		for contentByte in content:
			result.append(contentByte)
			checksum += contentByte
		result.append((checksum & 0x0000FF00) >> 8)
		result.append((checksum & 0x000000FF) >> 0)
		return result
