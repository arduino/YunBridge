##    This file is part of YunBridge.
##
##    Copyright 2015 Arduino LLC (http://www.arduino.cc/)
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

from socket import AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_REUSEADDR, SO_BROADCAST # SO_ERROR
from socket import gethostname
from select import select
import utils, socket


class UDPSocket:
  def __init__(self, address, port):
    self.txbuff = [ ]
    self.txmeta = [ ]
    self.rxbuff = [ ]
    self.rxmeta = [ ]
    self.curr_rxbuff = None
    self.curr_rxmeta = None
    self.curr_txbuff = None
    self.curr_txmeta = None
    self.sock = socket.socket(AF_INET, SOCK_DGRAM)
    self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    self.sock.setblocking(0)
    self.opened = False
    try:
      self.sock.bind((address, port))
      self.opened = True
    except socket.error, e:
      pass

  def run(self):
    rd, wr, err = select([self.sock], [self.sock], [self.sock], 0)

    if len(err) > 0:
      self.close()
      return

    # receive data from socket
    if len(rd) > 0:
      try:
        data, client = self.sock.recvfrom(1024)
      except:
        self.close()
        return
      self.rxbuff.append(data)
      self.rxmeta.append(client)

    # send data to socket
    if len(wr) > 0:
      if len(self.txbuff) > 0:
        try:
          self.sock.sendto(self.txbuff.pop(0), self.txmeta.pop(0))
        except socket.error, e:
          pass

  def recv_next(self):
    if len(self.rxbuff) == 0:
      return None
    self.curr_rxbuff = self.rxbuff.pop(0)
    self.curr_rxmeta = self.rxmeta.pop(0)
    return len(self.curr_rxbuff)

  def recv_address(self):
    if self.curr_rxbuff is None:
      return [None, None]
    if len(self.curr_rxbuff) == 0:
      return [None, None]
    return self.curr_rxmeta

  def recv(self, maxlen):
    if self.curr_rxbuff is None:
      return None
    if len(self.curr_rxbuff) > maxlen:
      res = self.curr_rxbuff[:maxlen]
      self.curr_rxbuff = self.curr_rxbuff[maxlen:]
    else:
      res = self.curr_rxbuff
      self.curr_rxbuff = ''
    return res

  def available(self):
    if self.curr_rxbuff is None:
      return None
    return len(self.curr_rxbuff)

  def send_start(self, address, port):
    self.curr_txbuff = ''
    self.curr_txmeta = (address, port)
    return True

  def send(self, data):
    if self.curr_txbuff is None:
      return None
    self.curr_txbuff += data
    return True

  def send_end(self):
    if self.curr_txbuff is None:
      return None
    self.txbuff.append(self.curr_txbuff)
    self.txmeta.append(self.curr_txmeta)
    self.curr_txbuff = None
    self.curr_txmeta = None
    return True

  def set_broadcast(self, v):
    if v:
      self.sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    else:
      self.sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 0)

  def close(self):
    self.sock.close()
    self.opened = False
    return True

  def is_opened(self):
    return self.opened

class UDPSocketsManager:
  def __init__(self):
    self.sockets = { }
    self.next_id = 0

  def run(self):
    for id in self.sockets:
      self.sockets[id].run()

  def create(self, address, port):
    # Determine the next id to assign to socket
    socket = UDPSocket(address, port)
    while self.next_id in self.sockets:
      self.next_id = (self.next_id + 1) % 256
    self.sockets[self.next_id] = socket
    return self.next_id

  def get(self, id):
    if not id in self.sockets:
      return None
    return self.sockets[id]

  def close(self, id):
    if not id in self.sockets:
      return None
    self.sockets[id].close()
    del self.sockets[id]
    return True

udp_sockets = UDPSocketsManager()

class CREATE_Command:
  def run(self, data):
    port = (ord(data[0]) << 8) + ord(data[1])
    id = udp_sockets.create(data[2:], port)
    if id is None:
      return chr(1) + chr(0)
    else:
      return chr(0) + chr(id)

class CLOSE_Command:
  def run(self, data):
    id = ord(data[0])
    udp_sockets.close(id)
    return ''

class WRITE_BEGIN_Command:
  def run(self, data):
    id = ord(data[0])
    sock = udp_sockets.get(id)
    if sock is None:
      return chr(0)
    port = (ord(data[1]) << 8) + ord(data[2])
    sock.set_broadcast(False)
    if sock.send_start(data[3:], port) is None:
      return chr(0)
    else:
      return chr(1)

class WRITE_BEGIN_BROADCAST_Command:
  def run(self, data):
    id = ord(data[0])
    sock = udp_sockets.get(id)
    if sock is None:
      return chr(0)
    port = (ord(data[1]) << 8) + ord(data[2])
    sock.set_broadcast(True)
    if sock.send_start('<broadcast>', port) is None:
      return chr(0)
    else:
      return chr(1)

class WRITE_Command:
  def run(self, data):
    id = ord(data[0])
    sock = udp_sockets.get(id)
    if sock is None:
      return chr(0)
    if sock.send(data[1:]) is None:
      return chr(0)
    else:
      return chr(1)

class WRITE_END_Command:
  def run(self, data):
    id = ord(data[0])
    sock = udp_sockets.get(id)
    if sock is None:
      return chr(0)
    if sock.send_end() is None:
      return chr(0)
    else:
      return chr(1)

class CLOSE_Command:
  def run(self, data):
    id = ord(data[0])
    server.close(id)
    return ''

class RECV_BEGIN_Command:
  def run(self, data):
    id = ord(data[0])
    sock = udp_sockets.get(id)
    if sock is None:
      return chr(0) + chr(0) + chr(0)
    l = sock.recv_next()
    if l is None:
      return chr(0) + chr(0) + chr(0)
    else:
      return chr(1) + chr((l >> 8) & 0xFF) + chr(l & 0xFF)

class RECV_Command:
  def run(self, data):
    id = ord(data[0])
    sock = udp_sockets.get(id)
    if sock is None:
      return chr(0)
    maxlen = ord(data[1])
    res = sock.recv(maxlen)
    if res is None:
      return ''
    else:
      return res

class AVAILABLE_Command:
  def run(self, data):
    id = ord(data[0])
    sock = udp_sockets.get(id)
    if sock is None:
      return chr(0)
    l = sock.available()
    if l is None:
      return chr(0) + chr(0) + chr(0)
    else:
      return chr(1) + chr((l >> 8) & 0xFF) + chr(l & 0xFF)

class REMOTE_IP_Command:
  def run(self, data):
    id = ord(data[0])
    sock = udp_sockets.get(id)
    if sock is None:
      return ''
    addr, port = sock.recv_address()
    if addr is None:
      return chr(0)
    addr = map(chr, map(int, addr.split('.')))
    return chr(1) + addr[0] + addr[1] + addr[2] + addr[3] + chr((port >> 8) & 0xff) + chr(port & 0xFF)

def init(command_processor):
  command_processor.register('e', CREATE_Command())
  command_processor.register('v', WRITE_BEGIN_BROADCAST_Command())
  command_processor.register('E', WRITE_BEGIN_Command())
  command_processor.register('h', WRITE_Command())
  command_processor.register('H', WRITE_END_Command())
  command_processor.register('q', CLOSE_Command())
  command_processor.register('Q', RECV_BEGIN_Command())
  command_processor.register('u', RECV_Command())
  command_processor.register('U', AVAILABLE_Command())
  command_processor.register('T', REMOTE_IP_Command())
  command_processor.register_runner(udp_sockets)

def test():
  from time import sleep
  import struct
  udp = UDPSocket('', 5555)
  udp.set_broadcast(True)
  udp.send_start('<broadcast>', 5555)
  udp.send('hi')
  udp.send_end()
  udp.set_broadcast(False)
  while True:
    udp.run()
    sleep(0.1)
    r = udp.recv_next()
    if r != None:
      addr, port = udp.recv_address()
      print "RECEIVED " + str(r) + " " + addr + ":" + str(port)
      data = udp.recv(4)
      data += udp.recv(1024)
      udp.send_start(addr, port)
      udp.send(data)
      udp.send_end()

if __name__ == '__main__':
  test()

