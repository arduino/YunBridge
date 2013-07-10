#!/usr/bin/python

import time

import packet
from packet import cbreak

class CommandProcessor:
  def __init__(self):
    self.commands = { }
    self.runners = [ ]
    self.finished = False
    
  def register_runner(self, runner):
    self.runners.append(runner)
    
  def register(self, key, command):
    self.commands[key] = command
         
  def run(self):
    for runner in self.runners:
      runner.run()
      
  def process(self, data):
    if data == 'XXXXX':
      print 'Goodbye...'
      self.finished = True
      return ''
      
    if data[0:2] == 'XX':
      for cmd in self.commands:
        if 'reset' in dir(cmd):
          cmd.reset()

    cmd = self.commands[data[0]]
    return cmd.run(data[1:])

cp = CommandProcessor()

import processes
processes.init(cp)

import console
console.init(cp)

import mailbox
mailbox.init(cp)

import files
files.init(cp)

import sockets
sockets.init(cp)

pr = packet.PacketReader(cp)
start_time = time.time()
with cbreak():
  #while time.time() - start_time < 100:
  while True:
    res = pr.process()
    if res == False:
      break

