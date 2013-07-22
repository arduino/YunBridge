#!/usr/bin/python

##    Copyright (c) 2013 Arduino LLC. All right reserved.
##
##    This library is free software; you can redistribute it and/or
##    modify it under the terms of the GNU Lesser General Public
##    License as published by the Free Software Foundation; either
##    version 2.1 of the License, or (at your option) any later version.
##
##    This library is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
##    Lesser General Public License for more details.
##
##    You should have received a copy of the GNU Lesser General Public
##    License along with this library; if not, write to the Free Software
##    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

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

