import unittest
import serial, time

class CRC:
  def __init__(self, serObj):
    self.result = 0xFFFF
    self.ser = serObj
    
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


class BaseBridgeTest(unittest.TestCase):
    def setUp(self):
       self.ser = serial.Serial()
       self.ser.baudrate = 115200
       self.ser.port = "/dev/ttyACM0"
       self.ser.open()
       self.ser.write("\n")
       time.sleep(1)
       self.ser.write("\n")
       time.sleep(1)
       self.ser.write("run-bridge\n")
       time.sleep(1)
       self.crc = CRC(self.ser) 

    def tearDown(self):
       message = 'XXXXX'
       self.crc.write('\xFF')
       self.crc.write('\x00')
       l = len(message)
       self.crc.write(chr(l >> 8))
       self.crc.write(chr(l & 0xFF))	
       self.crc.write(message)
       self.crc.write_crc()
       self.ser.close()
	
