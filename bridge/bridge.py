#!/usr/bin/python

##    This file is part of YunBridge.
##
##    YunBridge is free software; you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation; either version 2 of the License, or
##    (at your option) any later version.
##
##    This program is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License
##    along with this program; if not, write to the Free Software
##    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
##
##    As a special exception, you may use this file as part of a free software
##    library without restriction.  Specifically, if other files instantiate
##    templates or use macros or inline functions from this file, or you compile
##    this file and link it with other files to produce an executable, this
##    file does not by itself cause the resulting executable to be covered by
##    the GNU General Public License.  This exception does not however
##    invalidate any other reasons why the executable file might be covered by
##    the GNU General Public License.
##
##    Copyright 2013 Arduino LLC (http://www.arduino.cc/)

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

import sockets_udp
sockets_udp.init(cp)

pr = packet.PacketReader(cp)
start_time = time.time()
with cbreak():
  #while time.time() - start_time < 100:
  while True:
    res = pr.process()
    if res == False:
      break

