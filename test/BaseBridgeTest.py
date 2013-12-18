import unittest
import serial
import time


class CRC:
    def __init__(self, serObj):
        self.result = 0xFFFF
        self.ser = serObj
        self.count = 0

    def write(self, data):
        while len(data) > 0:
            if self.ser.isOpen():
                self.ser.write(data[0])
                tmp = data
                tmp = chr(ord(tmp[0]) ^ (self.result & 0xFF))
                tmp = chr(ord(tmp[0]) ^ ((ord(tmp[0]) << 4) & 0xFF))
                self.result = (((ord(tmp[0]) << 8) & 0xFFFF) | (self.result >> 8)) ^ ((ord(tmp[0]) >> 4) & 0xFF) ^ ((ord(tmp[0]) << 3) & 0xFFFF)
                data = data[1:]


    def write_crc(self):
        #print hex(self.result)
        self.ser.write(chr(self.result >> 8))
        self.ser.write(chr(self.result & 0xFF))

    def check(self, crc):
        #if self.result != crc:
        #  print 'CRC:' + hex(self.result) + '!' + hex(crc)
        return self.result == crc


class Dataclass:
    def __init__(self, serObj, crcObj):
        self.ser = serObj
        self.crc = crcObj

    def timedRead(self):
        c = self.ser.read()
        if c != "":
            print int(c)
            return int(c)
        else:
            return 0

    def transfer(self, message):
        print self.crc.write("\xFF")               #Start of Packet
        print self.crc.write(chr(self.crc.count))  #Message Index
        l = len(message)
        print self.crc.write(chr(l >> 8))          #Message length (hi)
        print self.crc.write(chr(l & 0xFF))        #Message length (lo)
        print self.crc.write(message)
        print self.crc.write_crc()
        self.crc.count = self.crc.count + 1  #Update message index

class BaseBridgeTest(unittest.TestCase):
    def setUp(self):
        self.ser = serial.Serial()
        self.ser.baudrate = 115200
        self.ser.port = "/dev/ttyACM0"
        self.ser.timeout = 0.005
        self.ser.open()
        self.ser.write("\n")
        time.sleep(1)
        self.ser.write("\n")
        time.sleep(1)
        self.ser.write("run-bridge\n")
        time.sleep(1)
        self.crc = CRC(self.ser)
        self.datas = Dataclass(self.ser, self.crc)
        print("Bridge started")             #uncomment to debug

    def tearDown(self):
        message = 'XXXXX'
        self.datas.transfer(message)
        print("Bridge closed")
        print self.ser.read(9999999)  #print the number of received bytes