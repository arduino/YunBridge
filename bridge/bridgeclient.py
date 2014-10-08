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
##    Copyright 2014 Arduino LLC (http://www.arduino.cc/)

from tcp import TCPJSONClient
from time import sleep


class BridgeClient:
  def __init__(self):
    self.json = None
    self.should_close_at_function_end = True

  def wait_response(self, json, timeout):
    while timeout >= 0:
      r = json.recv()
      if not r is None:
        return r
      timeout -= 0.1
      sleep(0.1)
    return None

  def wait_key(self, key, json, timeout):
    while True:
      r = self.wait_response(json, timeout)
      if r is None:
        return None
      try:
        if r['key'] == key:
          return r['value']
      except:
        pass

  def socket_open(self):
    if self.json is None:
      self.json = TCPJSONClient('127.0.0.1', 5700)
    return self.json

  def socket_close(self):
    if self.json is not None and self.should_close_at_function_end:
      self.json.close()
      self.json = None

  def begin(self):
    self.socket_open()
    self.should_close_at_function_end = False

  def close(self):
    self.should_close_at_function_end = True
    self.socket_close()

  def get(self, key):
    json = self.socket_open()
    json.send({'command': 'get', 'key': key})
    r = self.wait_key(key, json, 10)
    self.socket_close()
    return r

  def getall(self):
    json = self.socket_open()
    json.send({'command': 'get'})
    r = self.wait_response(json, 10)
    if not r is None:
      r = r['value']
    self.socket_close()
    return r

  def put(self, key, value):
    json = self.socket_open()
    json.send({'command': 'put', 'key': key, 'value': value})
    r = self.wait_key(key, json, 10)
    self.socket_close()
    return r

  def delete(self, key):
    json = self.socket_open()
    json.send({'command': 'delete', 'key': key})
    r = self.wait_response(json, 10)
    if not r is None and not r['value'] is None:
      r = r['value']
    self.socket_close()
    return r

  def mailbox(self, message):
    json = self.socket_open()
    json.send({'command': 'raw', 'data': message})
    self.socket_close()
