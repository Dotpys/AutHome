import machine
from micropython import const
import time

__ACK_OK = const(0x00)
__ACK_RECEPTION_ERROR = const(0x01)
__ACK_NO_FINGER = const(0x02)
__ACK_REGISTRATION_ERROR = const(0x03)
__ACK_IMAGE_TOO_NOISY = const(0x06)
__ACK_NOT_ENOUGH_CHAR = const(0x07)
__ACK_NOT_FOUND = const(0x09)
__ACK_NO_OTHER_PACKETS = const(0x0E)

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
__OPCODE_EMPTY = const(0x0D)
__OPCODE_SETSYSPARA = const(0x0E)
__OPCODE_READSYSPARA = const(0x0F)
__OPCODE_SETPWD = const(0x12)
__OPCODE_VFYPWD= const(0x13)
__OPCODE_GETRANDOMCODE = const(0x14)
__OPCODE_SETADDER = const(0x15)
__OPCODE_TEMPLATENUM = const(0x1D)
__OPCODE_READCONLIST = const(0x1F)

__PACKET_ID_COMMAND = const(0x01)
__PACKET_ID_DATA = const(0x02)
__PACKET_ID_RESPONSE = const(0x07)
__PACKET_ID_ENDDATA = const(0x08)

__PACKET_HEADER = b'\xEF\x01'

class FingerprintSensor:
    """
    Class used to interface with a fingerprint
    sensor trough serial communication.
    """

    __address = 0xFFFFFFFF
    __password = 0x00000000

    def __init__(self, tx: int, rx: int) -> None:
        self.channel = machine.UART(2)
        self.channel.init(
            baudrate=57600,
            bits=8,
            parity=None,
            stop=1,
            tx=tx,
            rx=rx,
            timeout=1000,
            timeout_char=1000)
        time.sleep_ms(500)


    #Instruction 0x01
    def generate_image(self):
        instruction_packet = self.generate_packet(__PACKET_ID_COMMAND, [__OPCODE_GENIMG])
        writtenBytes = self.channel.write(instruction_packet)
        response_packet = self.channel.read(12)
        #TODO: Add logging
        return response_packet[9]


    #Instruction 0x02
    def image_2_tz(self, buffer_id: int) -> int:
        if (buffer_id != 0x01):
            buffer_id = 0x02
        instruction_packet = self.generate_packet(__PACKET_ID_COMMAND, [__OPCODE_IMG2TZ, buffer_id])
        self.channel.write(instruction_packet)
        response_packet = self.channel.read(12)
        return response_packet[9]


    #Instruction 0x03
    def match(self) -> tuple[int, int]:
        instruction_packet = self.generate_packet(__PACKET_ID_COMMAND,[__OPCODE_MATCH])
        self.channel.write(instruction_packet)
        response_packet = self.channel.read(14)
        response_ack = response_packet[9]
        if (response_ack == __ACK_OK):
            return (response_ack, from_bytes(response_packet[10:2]))
        else:
            return (response_ack, [])


    #Instruction 0x04
    def search(self, buffer_id: int, start_page: int, page_number: int) -> tuple[int, int]:
        if(buffer_id != 0x01):
            buffer_id = 0X02
        content = [__OPCODE_SEARCH, buffer_id]
        content.append((start_page & 0xFF00) >> 8)
        content.append((start_page & 0x00FF) >> 0)
        content.append((page_number & 0xFF00) >> 8)
        content.append((page_number & 0x00FF) >> 0)
        instruction_packet = self.generate_packet(__PACKET_ID_COMMAND, content)
        self.channel.write(instruction_packet)
        response_packet = self.channel.read(16)
        response_ack = response_packet[9]
        if(response_ack == __ACK_OK):
            return (response_ack, from_bytes(response_packet[10:2]))
        else:
            return (response_ack, [])


    #Instruction 0x05
    def regModel(self) -> int:
        instruction_packet = self.generate_packet(__PACKET_ID_COMMAND, [__OPCODE_REGMODEL])
        self.channel.write(instruction_packet)
        response_packet = self.channel.read(12)
        return response_packet[9]


    #Instruction 0x06
    def store(self, bufferID: int, pageID) -> int:
        if(buffer_id != 0x01):
            buffer_id = 0X02
        content = [__OPCODE_STORE, bufferID]
        content.append((pageID & 0xFF00) >> 8)
        content.append((pageID & 0x00FF) >> 0)
        instruction_packet = self.generate_packet(__PACKET_ID_COMMAND, content)
        self.channel.write(instruction_packet)
        response_packet = self.channel.read(12)
        return response_packet[9]


    #Instruction 0x07
    def loadChar(self, bufferID: int, pageID: int) -> int:
        if(buffer_id != 0x01):
            buffer_id = 0X02
        content = [__OPCODE_LOADCHAR, bufferID]
        content.append((pageID & 0xFF00) >> 8)
        content.append((pageID & 0x00FF) >> 0)
        instruction_packet = self.generate_packet(__PACKET_ID_COMMAND, content)
        self.channel.write(instruction_packet)
        response_packet = self.channel.read(12)
        return response_packet[9]


      #Instruction 0x08
    
    #Instruction 0x08
    def upChar(self, bufferID: int) -> int:
        if(buffer_id != 0x01):
            buffer_id = 0X02
        content = [__OPCODE_UPCHAR, bufferID]
        instruction_packet = self.generate_packet(__PACKET_ID_COMMAND, content)
        self.channel.write(instruction_packet)
        response_packet = self.receive_packet(12)
        response_ack = response_packet[9]

        if (response_ack == __ACK_OK):
            print("Sending characteristics to host...")
            characteristics: bytes = []
            end: bool = False
            while (not end):
                data_packet = self.receive_packet()

                if(data_packet ["id"] == __PACKET_ID_ENDDATA):
                    end = True
                characteristics += data_packet["data"]
            return (response_ack, characteristics)
        else:
            return (response_ack, [])


    #Instruction 0x09
    def download_char(self, bufferID: int) -> tuple[int, int]:
        content = [__OPCODE_DOWNCHAR, bufferID]
        instruction_packet = self.generate_packet(__PACKET_ID_COMMAND, content)
        self.channel.write(instruction_packet)
        response_packet = self.channel.read(12)
        response_ack = response_packet(9)

        if(response_ack == __ACK_OK):
            characteristic: bytes = []
            end: bool = False
            while(not end):
                data_packet = self.receive_packet()
                if(data_packet["id"] == __PACKET_ID_ENDDATA):
                    end = True
                characteristic += (data_packet["data"])
            return (response_ack, characteristic)
        else:
            return (response_ack, [])


    #Instruction 0x0A
    def upload_image(self) -> tuple[int, bytes]:
        """
        Il modulo di impronta carica i dati dell'immagine dal buffer di immagini.
        """
        #Sends the instruction packet
        instruction_packet = self.generate_packet(__PACKET_ID_COMMAND, [__OPCODE_UPIMAGE])
        self.channel.write(instruction_packet)

        #Receives the response packet
        response_packet = self.receive_packet()
        response_ack = response_packet["data"][0]

        if (response_ack == __ACK_OK):
            print("Receiving data from fingerprint module...")
            image_data: bytes = []
            end: bool = False
            while (not end):
                data_packet = self.receive_packet()

                if (data_packet["id"] == __PACKET_ID_ENDDATA):
                    end = True
                image_data += (data_packet["data"])
                print("Received " + str(len(image_data)) + " Bytes")
            print("Image size: " + str(len(image_data)) + " Bytes")
            return (response_ack, image_data)
        else:
            return (response_ack, [])


    #Instruction 0x0F
    def read_system_parameters(self):
        instruction_packet = self.generate_packet(__PACKET_ID_COMMAND, [__OPCODE_READSYSPARA])
        self.channel.write(instruction_packet)
        response_packet = self.channel.read(28)
        return ReadSysParaResponseType.deserialize(response_packet[10:27])


    def generate_packet(self, packet_id, content):
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


    def receive_packet(self):
        packet_header = self.channel.read(9)
        baotou = int.from_bytes(packet_header[0:2], 'big')
        address = int.from_bytes(packet_header[2:6], 'big')
        packet_id = int.from_bytes(packet_header[6:7], 'big')
        packet_size = int.from_bytes(packet_header[7:9], 'big')
        packet_data = self.channel.read(packet_size-2)
        packet_checksum = int.from_bytes(self.channel.read(2), 'big')
        return {
            "baotou": baotou,
            "address": address,
            "id": packet_id,
            "size": packet_size,
            "data": packet_data,
            "checksum": packet_checksum
        }


class ReadSysParaResponseType:
    """
    Represents the data structure sent
    by the fingerprint sensor to respond
    to a ReadSysParam command.
    """

    state_register = 0
    system_id = 0
    lib_size = 0
    security_level = 0
    device_address = 0
    packet_address = 0
    transmission_speed = 0

    @classmethod
    def deserialize(cls, data: bytearray):
        result: ReadSysParaResponseType = ReadSysParaResponseType()
        result.state_register = int.from_bytes(data[0:2], 'big')
        result.system_id = int.from_bytes(data[2:4], 'big')
        result.lib_size = int.from_bytes(data[4:6], 'big')
        result.security_level = int.from_bytes(data[7:8], 'big')
        result.device_address = int.from_bytes(data[8:12], 'big')
        result.packet_address = int.from_bytes(data[12:14], 'big')
        result.transmission_speed = int.from_bytes(data[14:16], 'big')
        return result


#fs = FingerprintSensor(rx=14, tx=12)
#fs.search(4, 0x1234, 0x6543)
#print("Sensore di imprtonta inizializzato")
#result: int = 0
#print("Appoggia il dito")
#while (True):
#    result = fs.generate_image()
#    if (result == __ACK_OK):
#        break
#print("Impronta riconosciuta, provo a scaricarla...")
#dat = fs.upload_image()

#ZFM-20