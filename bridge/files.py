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

class Files:
  def __init__(self):
    self.files = { }
    self.next_id = 0
    
  def open(self, filename, mode):
    # Open file
    try:
      file = open(filename, mode)
    except IOError, e:
      return [e.errno, None]
    
    # Determine the next id to assign to file
    while self.next_id in self.files:
      self.next_id = (self.next_id + 1) % 256
    self.files[self.next_id] = file
    return [0, self.next_id]
    
  def close(self, id):
    if id not in self.files:
      return
    file = self.files[id]
    try:
      file.close()
    except:
      pass
    del self.files[id]
  
  def read(self, id, maxlen):
    if id not in self.files:
      return None
    file = self.files[id]
    try:
      return [0, file.read(maxlen)]
    except IOError, e:
      return [e.errno, None]

  def write(self, id, data):
    if id not in self.files:
      return None
    file = self.files[id]
    try:
      file.write(data)
      file.flush()
      return 0
    except IOError, e:
      return e.errno

  def seek(self, id, pos):
    if id not in self.files:
      return None
    file = self.files[id]
    try:
      file.seek(pos)
      return 0
    except IOError, e:
      return e.errno
    
  def tell(self, id):
    if id not in self.files:
      return [None, None]
    file = self.files[id]
    try:
      return [0, file.tell()]
    except IOError, e:
      return [e.errno, None]

  def isDir(self, filename):
    from os import path
    return path.isdir(filename)
        
  def size(self, id):
    from os import SEEK_END, SEEK_SET
    if id not in self.files:
      return [None, None]
    file = self.files[id]
    try:
      old_position = file.tell()
      file.seek(0, SEEK_END)
      size = file.tell()
      file.seek(old_position, SEEK_SET)
      return [0, size]
    except IOError, e:
      return [e.errno, None]
      
files = Files()

class OPEN_Command:
  def run(self, data):
    [err, id] = files.open(data[1:], data[0]+'b')
    if err!=0:
      return chr(err) + chr(0)
    else:
      return chr(0) + chr(id)

class CLOSE_Command:
  def run(self, data):
    id = ord(data[0])
    files.close(id)
    return '\x00'
      
class READ_Command:
  def run(self, data):
    id = ord(data[0])
    maxlen = ord(data[1])
    [err, res] = files.read(id, maxlen)
    if err!=0:
      return chr(err)
    else:
      return chr(0) + res

class WRITE_Command:
  def run(self, data):
    id = ord(data[0])
    data = data[1:]
    err = files.write(id, data)
    return chr(err)
    
class SEEK_Command:
  def run(self, data):
    id = ord(data[0])
    pos =  ord(data[1]) << 24
    pos += ord(data[2]) << 16
    pos += ord(data[3]) << 8
    pos += ord(data[4])
    err = files.seek(id, pos)
    return chr(err)

class TELL_Command:
  def run(self, data):
    id = ord(data[0])
    [err, pos] = files.tell(id)
    if pos is None:
      pos = 0
      err = 255
    if err is None:
      err = 255
    res = chr(err)
    res += chr((pos>>24) & 0xFF)
    res += chr((pos>>16) & 0xFF)
    res += chr((pos>>8) & 0xFF)
    res += chr(pos & 0xFF)
    return res

class SIZE_Command:
  def run(self, data):
    id = ord(data[0])
    [err, size] = files.size(id)
    if size is None:
      size = 0
    if err is None:
      err = 255
    res = chr(err)
    res += chr((size>>24) & 0xFF)
    res += chr((size>>16) & 0xFF)
    res += chr((size>>8) & 0xFF)
    res += chr(size & 0xFF)
    return res


class ISDIRECTORY_Command:
  def run(self, data):
    filename = data[0:]
    if files.isDir(filename) is True:
      return chr(1)
    else:
      return chr(0)


    
def init(command_processor):
  command_processor.register('F', OPEN_Command())
  command_processor.register('f', CLOSE_Command())
  command_processor.register('G', READ_Command())
  command_processor.register('g', WRITE_Command())
  command_processor.register('i', ISDIRECTORY_Command())
  command_processor.register('s', SEEK_Command())
  command_processor.register('S', TELL_Command())
  command_processor.register('t', SIZE_Command())
  
