import subprocess
import sys, time
import bridge.packet
import atexit
import unittest
import AbstractBridgeTest

class TestSequenceFunctions(AbstractBridgeTest.BridgeTest):
        
    def test_shutdown(self):
        message = 'XXXXX'
        sys.stderr.write("Sending shutdown command.\n")
        self.crc.write('\xFF')
        self.crc.write('\x00')
        l = len(message)
        self.crc.write(chr(l >> 8))
        self.crc.write(chr(l & 0xFF))	
        self.crc.write(message)
        self.crc.write_crc()
        self.bridge.stdin.flush()
        time.sleep(1)
        self.assertEqual(self.bridge.poll(),None)
	  
if __name__ == '__main__':
    unittest.main()
