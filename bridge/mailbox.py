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

from tcp import TCPJSONServer
from collections import deque
import streamingjson

json_server = TCPJSONServer('127.0.0.1', 5700)

class Mailbox:
  def __init__(self):
    self.incoming = deque()
    self.data_store = { }

  def run(self):
    json_server.run()
    if json_server.available() > 0:
      try:
        self.ext_command(json_server.read())
      except:
        pass

  def ext_command(self, msg):
    if not 'command' in msg:
      return
    command = msg['command']

    if command == 'raw':
      self.incoming.append(msg['data'])
      return

    if command == 'get':
      if msg.has_key('key'):
        k = msg['key']
        v = self.data_store_get(k)
        json_server.write({ 'response' : 'get', 'key' : k, 'value' : v })
      else:
        json_server.write({ 'response' : 'get', 'value' : self.data_store })
      return

    if command == 'put':
      k = msg['key']
      v = msg['value']
      self.data_store_put(k, v)
      json_server.write({ 'response' : 'put', 'key' : k, 'value' : v })
      return

    if command == 'delete':
      k = msg['key']
      v = self.data_store_get(k)
      if v:
        self.data_store_delete(k)
        json_server.write({ 'response' : 'delete', 'key' : k, 'value' : v })
      else:
        json_server.write({ 'response' : 'delete', 'key' : k })
      return

  def data_store_put(self, k, v):
    self.data_store[k] = v
    
  def data_store_delete(self, k):
    del self.data_store[k]
    
  def data_store_get(self, k):
    if k in self.data_store:
      return self.data_store[k]
    else:
      return None
      
  def send(self, data):
    json_server.write({ 'request' : 'raw', 'data' : data })
    
  def recv(self):
    if len(self.incoming) > 0:
      return self.incoming.popleft()
    return None
            
  def peek(self):
    if len(self.incoming) > 0:
      return self.incoming[0]
    else:
      return None
    
mailbox = Mailbox()

class SEND_Command:
  def run(self, data):
    mailbox.send(data)
    return ''

class SEND_JSON_Command:
  def run(self, data):
    try:
      obj, i = streamingjson.read(data)
      mailbox.send(obj)
    except:
      mailbox.send(data)
    return ''

class RECV_Command:
  def run(self, data):
    msg = mailbox.recv()
    if msg is None:
      return ''
    else:
      return msg

class AVAILABLE_Command:
  def run(self, data):
    msg = mailbox.peek()
    if msg is None:
      return '\x00\x00'
    else:
      l = (len(msg) >> 8) & 0xFF
      h = len(msg) & 0xff
      return chr(l) + chr(h)

class DATASTORE_GET_Command:
  def run(self, data):
    res = mailbox.data_store_get(data)
    if res is None:
      return ''
    else:
      return res
    
class DATASTORE_PUT_Command:
  def run(self, data):
    v = data.split('\xFE')
    if len(v)!=2:
      return '\x00'
    mailbox.data_store_put(v[0], v[1])
    return '\x01'
    
def init(command_processor):
  command_processor.register('M', SEND_Command())
  command_processor.register('J', SEND_JSON_Command())
  command_processor.register('m', RECV_Command())
  command_processor.register('n', AVAILABLE_Command())
  command_processor.register('D', DATASTORE_PUT_Command())
  command_processor.register('d', DATASTORE_GET_Command())
  command_processor.register_runner(mailbox)

