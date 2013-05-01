#!/usr/bin/python

import time

import processes
import packet
from packet import cbreak

class CommandProcessor:
  def __init__(self):
    self.commands = { }
  
  def register(self, key, command):
    self.commands[key] = command
         
  def process(self, data):
    if data=='XX':
      for cmd in self.commands:
        if "reset" in dir(cmd):
          cmd.reset()
      return ""
      
    cmd = self.commands[data[0]]
    return cmd.run(data[1:])

cp = CommandProcessor()
processes.init(cp)

pr = packet.PacketReader(cp)
start_time = time.time()
with cbreak():
  while time.time() - start_time < 100:
    res = pr.process()
    if res == False:
      break

