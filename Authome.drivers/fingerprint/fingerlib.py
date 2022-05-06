import numpy as np
import serial
from PIL import Image
import numpy as np

ACK_OK: int = 0x00
ACK_RECEPTION_ERROR: int = 0x01
ACK_NO_FINGER: int = 0x02
ACK_REGISTRATION_ERROR: int = 0x03
ACK_IMAGE_TOO_NOISY: int = 0x06
ACK_NOT_ENOUGH_CHAR: int = 0x07
ACK_NOT_FOUND: int = 0x09
ACK_NO_OTHER_PACKETS: int = 0x0E

OPCODE_GENIMG: int = 0x01
OPCODE_IMG2TZ: int = 0x02
OPCODE_MATCH: int = 0x03
OPCODE_SEARCH: int = 0x04
OPCODE_REGMODEL: int = 0x05
OPCODE_STORE: int = 0x06
OPCODE_LOADCHAR: int = 0x07
OPCODE_UPCHAR: int = 0x08
OPCODE_DOWNCHAR: int = 0x09
OPCODE_UPIMAGE: int = 0x0A
#0x0B, 0x0C
OPCODE_EMPTY: int = 0x0D
OPCODE_SETSYSPARA: int = 0x0E
OPCODE_READSYSPARA: int = 0x0F
OPCODE_SETPWD: int = 0x12
OPCODE_VFYPWD: int = 0x13
OPCODE_GETRANDOMCODE: int = 0x14
OPCODE_SETADDER: int = 0x15
#0x16, 0x17, 0x18, 0x19, 0x1A, 0x1B, 0x1C
OPCODE_TEMPLATENUM: int = 0x1D
OPCODE_READCONLIST: int = 0x1F

PACKET_ID_COMMAND: int = 0x01
PACKET_ID_DATA: int = 0x02
PACKET_ID_RESPONSE: int = 0x07
PACKET_ID_ENDDATA: int = 0x08

class FingerprintSensor:
    """
    Class used to interface with a fingerprint
    sensor trough serial communication.
    """

    address: np.uint32 = 0xFFFFFFFF
    channel: serial.Serial

    def __init__(self, serialPort: str, baudrate: int) -> None:
        self.channel = serial.Serial(serialPort)
        self.channel.baudrate = baudrate


    #Instruction 0x01
    def generate_image(self) -> int:
        instruction_packet = self.generate_packet(PACKET_ID_COMMAND, [OPCODE_GENIMG])
        self.channel.write(instruction_packet)
        response_packet = self.channel.read(12)
        return response_packet[9]


    #Instruction 0x02
    def image_2_tz(self, buffer_id: int) -> int:
        if (buffer_id != 0x01):
            buffer_id = 0x02
        instruction_packet = self.generate_packet(PACKET_ID_COMMAND, [OPCODE_IMG2TZ, buffer_id])
        self.channel.write(instruction_packet)
        response_packet = self.channel.read(12)
        return response_packet[9]


    #Instruction 0x03
    def match(self) -> tuple[int, int]:
        instruction_packet = self.generate_packet(PACKET_ID_COMMAND,[OPCODE_MATCH])
        self.channel.write(instruction_packet)
        response_packet = self.channel.read(14)
        response_ack = response_packet[9]
        if (response_ack == ACK_OK):
            return (response_ack, from_bytes(response_packet[10:2]))
        else:
            return (response_ack, [])


    #Instruction 0x04
    def search(self, buffer_id: int, start_page: int, page_number: int) -> tuple[int, int]:
        if(buffer_id != 0x01):
            buffer_id = 0X02
        content = [OPCODE_SEARCH, buffer_id]
        content.append((start_page & 0xFF00) >> 8)
        content.append((start_page & 0x00FF) >> 0)
        content.append((page_number & 0xFF00) >> 8)
        content.append((page_number & 0x00FF) >> 0)
        instruction_packet = self.generate_packet(PACKET_ID_COMMAND, content)
        self.channel.write(instruction_packet)
        response_packet = self.channel.read(16)
        response_ack = response_packet[9]
        if(response_ack == ACK_OK):
            return (response_ack, from_bytes(response_packet[10:2]))
        else:
            return (response_ack, [])


    #Instruction 0x05
    def regModel(self) -> int:
        instruction_packet = self.generate_packet(PACKET_ID_COMMAND, [OPCODE_REGMODEL])
        self.channel.write(instruction_packet)
        response_packet = self.channel.read(12)
        return response_packet[9]


    #Instruction 0x06
    def store(self, bufferID: int, pageID) -> int:
        if(buffer_id != 0x01):
            buffer_id = 0X02
        content = [OPCODE_STORE, bufferID]
        content.append((pageID & 0xFF00) >> 8)
        content.append((pageID & 0x00FF) >> 0)
        instruction_packet = self.generate_packet(PACKET_ID_COMMAND, content)
        self.channel.write(instruction_packet)
        response_packet = self.channel.read(12)
        return response_packet[9]


    #Instruction 0x07
    def loadChar(self, bufferID: int, pageID: int) -> int:
        if(buffer_id != 0x01):
            buffer_id = 0X02
        content = [OPCODE_LOADCHAR, bufferID]
        content.append((pageID & 0xFF00) >> 8)
        content.append((pageID & 0x00FF) >> 0)
        instruction_packet = self.generate_packet(PACKET_ID_COMMAND, content)
        self.channel.write(instruction_packet)
        response_packet = self.channel.read(12)
        return response_packet[9]


    #Instruction 0x09
    def downChar(self, bufferID: int) -> tuple[int, int]:
        content = [OPCODE_DOWNCHAR, bufferID]
        instruction_packet = self.generate_packet(PACKET_ID_COMMAND, content)
        self.channel.write(instruction_packet)
        response_packet = self.channel.read(12)
        response_ack = response_packet(9)

        if(response_ack == ACK_OK):
            characteristic: bytes = []
            end: bool = False
            while(not end):
                data_packet = self.receive_packet()
                if(data_packet["id"] == PACKET_ID_ENDDATA):
                    end = True
                characteristic += (data_packet["data"])
            return (response_ack, characteristic)
        else:
            return (response_ack, [])


    #Instruction 0x0A
    def upload_image(self) -> tuple[int, bytes]:
        """
        Il computer host scarica i dati dell'immagine dal buffer
        di immagini del modulo.
        """
        #Sends the instruction packet
        instruction_packet = self.generate_packet(0x01, [OPCODE_UPIMAGE])
        self.channel.write(instruction_packet)

        #Receives the response packet
        response_packet = self.receive_packet()
        response_ack = response_packet["data"][0]

        if (response_ack == ACK_OK):
            print("Receiving data from fingerprint module...")
            image_data: bytes = []
            end: bool = False
            while (not end):
                data_packet = self.receive_packet()

                if (data_packet["id"] == PACKET_ID_ENDDATA):
                    end = True
                image_data += (data_packet["data"])
                print("Received " + str(len(image_data)) + " Bytes")
            print("Image size: " + str(len(image_data)) + " Bytes")
            return (response_ack, image_data)
        else:
            return (response_ack, [])


    #Instruction 0x0F
    def read_system_parameters(self) -> None:
        instruction_packet = self.generate_packet(0x01, [0x0f])
        self.channel.write(instruction_packet)
        response_packet = self.channel.read(28)
        return ReadSysParaResponseType.deserialize(response_packet[10:27])


    def generate_packet(self, packet_id: bytes, content: bytes) -> bytes:
        result = [0xEF, 0x01]
        result.append((self.address & 0xFF000000) >> 24)
        result.append((self.address & 0x00FF0000) >> 16)
        result.append((self.address & 0x0000FF00) >>  8)
        result.append((self.address & 0x000000FF) >>  0)
        result.append(packet_id)
        checksum: np.ushort = packet_id
        length: np.ushort = len(content) + 2
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

    def send_packet(self, packet_data: bytes):
        pass

    def receive_packet(self) -> bytes:
        packet_header = self.channel.read(9)
        baotou = from_bytes(packet_header[0:2])
        address = from_bytes(packet_header[2:6])
        packet_id = from_bytes(packet_header[6:7])
        packet_size = from_bytes(packet_header[7:9])
        packet_data = self.channel.read(packet_size-2)
        packet_checksum = from_bytes(self.channel.read(2))
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

    state_register: np.uint16
    system_id: np.uint16
    lib_size: np.uint16
    security_level: np.uint16
    device_address: np.uint32
    packet_address: np.uint16
    transmission_speed: np.uint16

    @classmethod
    def deserialize(cls, data: bytearray):
        result: ReadSysParaResponseType = ReadSysParaResponseType()
        result.state_register = from_bytes(data[0:2])
        result.system_id = from_bytes(data[2:4])
        result.lib_size = from_bytes(data[4:6])
        result.security_level = from_bytes(data[7:8])
        result.device_address = from_bytes(data[8:12])
        result.packet_address = from_bytes(data[12:14])
        result.transmission_speed = from_bytes(data[14:16])
        return result


def from_bytes(data: bytearray) -> int:
    return int.from_bytes(bytes=data, byteorder='big', signed=False)


fs = FingerprintSensor("COM4", 57600)
fs.search(4, 0x1234, 0x6543)
print("Sensore di imprtonta inizializzato")
result: int = 0
print("Appoggia il dito")
while (True):
    result = fs.generate_image()
    if (result == 0):
        break
print("Impronta riconosciuta, provo a scaricarla...")
dat = fs.upload_image()
extended_data: bytes = []
for b in dat[1]:
    extended_data.append(b&0b11110000)
    extended_data.append((b & 0b00001111)<<4)
#image_data = np.frombuffer(extended_data, np.uint8)
image_data = np.reshape(extended_data, (256, 288))

img = Image.frombuffer("L", (256, 288), image_data.astype(np.uint8))
img.save("Test.bmp")