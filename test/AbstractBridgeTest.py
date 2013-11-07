import subprocess
import sys, time
import atexit
import bridge.packet
import unittest

class BridgeTest(unittest.TestCase):
    def setUp(self):
        args = ['python', '-u', 'bridge/bridge.py']
        self.bridge = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=open("/home/arturo/Scrivania/logBridgeTest.txt", "w"))          
        self.crc = bridge.packet.CRC(self.bridge.stdin)

