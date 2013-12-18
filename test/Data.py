import serial
import time
from BaseBridgeTest import CRC

class Data:
    def timedRead(self, timeout):
        sera = serial()
        start_time = time.time()
        while (time.time() - start_time < timeout):
            c = sera.read()
            if c >= 0:
                self.result = c
            else:
                self.result = -1

            return self.result


    def transfer(self, message):
        crc = CRC(self.ser)
        crc.write("0xFF")               #Start of Packet
        crc.write(chr(self.count))      #Message Index
        l = len(message)
        crc.write(chr(l >> 8) & 0xFF)   #Message length (hi)
        crc.write(chr(l & 0xFF))        #Message length (lo)
        crc.write(message)
        crc.write_crc()
        self.ser.flush()
        if self.timedRead(100) != 0xFF:
            crc.crcReset()
        a = self.timedRead(5)
        lh = self.timedRead(5)
        ll = self.timedRead(5)
        l = lh
        l <<= 8
        l += ll
        for i in range(0, l):
            c = self.timedRead(5)

        crc_hi = self.timedRead(5)
        crc_lo = self.timedRead(5)

        self.count = self.count + 1     #Update message index