import subprocess
import sys, os, time
import atexit
import bridge.packet
import unittest

class BridgeTest(unittest.TestCase):
    def setUp(self):
	directory = os.getcwd()
	if (directory[len(directory)-9:len(directory)] == "YunBridge"):
        	args = ['python', '-u', 'bridge/bridge.py']
	if (directory[len(directory)-6:len(directory)] == "bridge"):
		args = ['python', '-u', 'bridge.py']
	if (directory[len(directory)-4:len(directory)] == "test"):
		args = ['python', '-u', '../bridge/bridge.py']
        self.bridge = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=open("test/logTest.txt", "w"))          
        self.crc = bridge.packet.CRC(self.bridge.stdin)

