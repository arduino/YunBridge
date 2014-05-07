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

from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR, gethostname
from select import select
from collections import deque
import streamingjson
import utils


class TCPClient:
  def __init__(self, address, port):
    client = socket(AF_INET, SOCK_STREAM)
    client.connect((address, port))
    self.socket = client
  
  def send(self, data):
    try:
      while len(data) > 0:
        l = self.socket.send(data)
        data = data[l:]
    except:
      pass
  
  def recv(self):
    rd, wr, err = select([self.socket], [], [], 0)
    if len(rd) > 0:
      return self.socket.recv(4096)
    return None

  def close(self):
    self.socket.close()
    
class TCPJSONSender(TCPClient):
  def send(self, obj):
    data = streamingjson.write(obj)
    TCPClient.send(self, data)
    
class TCPJSONClient(TCPJSONSender):
  def __init__(self, address, port):
    TCPClient.__init__(self, address, port)
    self.recvbuff = ''

  def recv(self):
    self.recvbuff = TCPClient.recv(self)
    # try to stream-decode received data
    try:
      if len(self.recvbuff) > 0:
        res, i = streamingjson.read(self.recvbuff)
        self.recvbuff = self.recvbuff[i:].lstrip()
        return res
    except:
      # incomplete data...
      pass
    return None

class TCPServer:
  def __init__(self, address, port):
    server = socket(AF_INET, SOCK_STREAM)
    server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    utils.try_bind(server, address, port)
    server.listen(5)
    server.setblocking(0)
    self.server = server
    self.clients = [ ]
    self.clients_sendbuffer = { }
    self.clients_recvbuffer = { }
    self.sockets = [ server ]

  def run(self):
    rd, wr, err = select(self.sockets, [], self.sockets, 0)

    # Accept new connections
    if self.server in rd:
      self.accept()
      rd.remove(self.server)

    # Read from sockets
    for sock in rd:
      self.socket_receive(sock)

    # Write buffers to sockets
    rd, wr, err = select([], self.clients, [], 0)
    for client in wr:
      try:
        buff = self.clients_sendbuffer[client]
        if len(buff) > 0:
          sent = client.send(buff)
          self.clients_sendbuffer[client] = buff[sent:]
      except:
        self.close(client)
    
    # Drop starving clients
    for client in self.clients:
      if len(self.clients_sendbuffer[client]) > 8192:
        self.close(client)

  def socket_receive(self, client):
    try:
      chunk = client.recv(4096)
      if chunk == '':
        self.close(client)
        return
      chunk = self.clients_recvbuffer[client] + chunk
      self.clients_recvbuffer[client] = self.recv(chunk)
    except:
      self.close(client)

  def recv(self, data):
    # Default server consumes all data
    return ''

  def send(self, data):
    # send chunk to all clients
    for c in self.clients:
      self.clients_sendbuffer[c] += data
     
  def accept(self):
    (client, address) = self.server.accept()
    self.sockets.append(client)
    self.clients.append(client)
    self.clients_sendbuffer[client] = ''
    self.clients_recvbuffer[client] = ''

  def close(self, sock):
    sock.close()
    self.clients.remove(sock)
    self.sockets.remove(sock)
    del self.clients_sendbuffer[sock]
    del self.clients_recvbuffer[sock]

class TCPJSONServer(TCPServer):
  def __init__(self, port, address='127.0.0.1'):
    TCPServer.__init__(self, port, address)
    self.recv_queue = deque()

  def recv(self, data):
    # try to stream-decode received data
    try:
      while len(data) > 0:
        res, i = streamingjson.read(data)
        self.recv_queue.append(res)
        data = data[i:].lstrip()
    except:
      # incomplete data...
      pass
    return data

  def available(self):
    return len(self.recv_queue) > 0

  def read(self):
    try:
      return self.recv_queue.popleft()
    except IndexError:
      return None

  def write(self, obj):
    data = streamingjson.write(obj)
    self.send(data)

# Test
if __name__ == '__main__':
  bus = TCPJSONReceiver('0.0.0.0', 12345)
  while True:
    bus.run()
    data = bus.read()
    if not data is None:
      print data

