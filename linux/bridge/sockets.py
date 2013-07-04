from socket import AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR, SO_ERROR
from socket import gethostname
from select import select
import utils, socket


class SocketClient:
  def __init__(self, sock):
    self.sock = sock
    self.txbuff = ''
    self.rxbuff = ''
    self.connected = True
    self.connecting = False

  def __init__(self, address, port):
    self.txbuff = ''
    self.rxbuff = ''
    self.connected = False
    self.connecting = True

    self.sock = socket.socket(AF_INET, SOCK_STREAM)
    self.sock.setblocking(0)
    try:
      self.sock.connect((address, port))
    except socket.error, e:
      pass

  def run(self):
    if self.connecting:
      rd, wr, err = select([], [self.sock], [self.sock], 0)
      if len(wr)>0:
        self.connecting = False
        self.connected = True
        connect_result = self.sock.getsockopt(SOL_SOCKET, SO_ERROR)
        if connect_result != 0:
          self.close()
          return
      if len(err)>0:
        self.close()
        return
    if not self.connected:
      return

    rd, wr, err = select([self.sock], [self.sock], [self.sock], 0)

    if len(err) > 0:
      self.close()
      return

    # receive data from socket
    if len(rd) > 0:
      if len(self.rxbuff)<1024:
        try:
          chunk = self.sock.recv(1024)
        except:
          self.close()
          return
        if chunk == '':
          self.close()
          return
        self.rxbuff += chunk
        
    # send data to socket
    if len(wr) > 0:
      if len(self.txbuff) > 0:
        sent = self.sock.send(self.txbuff)
        self.txbuff = self.txbuff[sent:]

  def recv(self, maxlen):
    if len(self.rxbuff) == 0:
      return ''
    if len(self.rxbuff) > maxlen:
      res = self.rxbuff[:maxlen]
      self.rxbuff = self.rxbuff[maxlen:]
    else:
      res = self.rxbuff
      self.rxbuff = ''
    return res

  def send(self, data):
    self.txbuff += data

  def close(self):
    self.sock.close()
    self.connected = False
    self.connecting = False

  def is_connected(self):
    return self.connected

  def is_connecting(self):
    return self.connecting

class SocketServer:
  def __init__(self):
    self.server = None
    self.clients = { }
    self.next_id = 0

  def run(self):
    for id in self.clients:
      self.clients[id].run()

  def connect(self, address, port):
    # Determine the next id to assign to socket
    client = SocketClient(address, port)
    while self.next_id in self.clients:
      self.next_id = (self.next_id + 1) % 256
    self.clients[self.next_id] = client
    return self.next_id
    
  def listen(self, address, port):
    if not self.server is None:
      self.server.close()
      self.server = None
    try:
      server = socket.socket(AF_INET, SOCK_STREAM)
      server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
      utils.try_bind(server, address, port)
      server.listen(1) # No connection backlog
      server.setblocking(0)
      self.server = server
      return True
    except:
      return False

  def accept(self):
    if self.server is None:
      return None

    rd, wr, err = select([self.server], [], [], 0)
    if len(rd) == 0:
      return None

    # Accept new connections
    (client_sock, address) = self.server.accept()
    # IP filtering could be here
    client = SocketClient(client_sock)
    
    # Determine the next id to assign to socket
    while self.next_id in self.clients:
      self.next_id = (self.next_id + 1) % 256
    self.clients[self.next_id] = client
    return self.next_id

  def recv(self, id, maxlen):
    if not id in self.clients:
      return None
    return self.clients[id].recv(maxlen)

  def send(self, id, data):
    if not id in self.clients:
      return None
    self.clients[id].send(data)
    return True
     
  def is_connected(self, id):
    if not id in self.clients:
      return None
    return self.clients[id].is_connected()

  def is_connecting(self, id):
    if not id in self.clients:
      return None
    return self.clients[id].is_connecting()

  def close(self, id):
    if not id in self.clients:
      return None
    self.clients[id].close()
    del self.clients[id]
    return True
    
server = SocketServer()

class LISTEN_Command:
  def run(self, data):
    port = (ord(data[0]) << 8) + ord(data[1])
    if server.listen(data[2:], port):
      return '\x01'
    else:
      return '\x00'

class CONNECT_Command:
  def run(self, data):
    port = (ord(data[0]) << 8) + ord(data[1])
    c = server.connect(data[2:], port)
    if c is None:
      return ''
    else:
      return chr(c)

class ACCEPT_Command:
  def run(self, data):
    c = server.accept()
    if c is None:
      return ''
    else:
      return chr(c)

class WRITE_Command:
  def run(self, data):
    id = ord(data[0])
    server.send(id, data[1:])
    return ''

class READ_Command:
  def run(self, data):
    id = ord(data[0])
    len = ord(data[1])
    res = server.recv(id, len)
    if res is None:
      return ''
    else:
      return res
    
class CONNECTED_Command:
  def run(self, data):
    id = ord(data[0])
    if server.is_connected(id):
      return '\x01'
    else:
      return '\x00'
      
class CONNECTING_Command:
  def run(self, data):
    id = ord(data[0])
    if server.is_connecting(id):
      return '\x01'
    else:
      return '\x00'

class CLOSE_Command:
  def run(self, data):
    id = ord(data[0])
    server.close(id)
    return ''

def init(command_processor):
  command_processor.register('N', LISTEN_Command())
  command_processor.register('k', ACCEPT_Command())
  command_processor.register('K', READ_Command())
  command_processor.register('l', WRITE_Command())
  command_processor.register('L', CONNECTED_Command())
  command_processor.register('j', CLOSE_Command())
  command_processor.register('c', CONNECTING_Command())
  command_processor.register('C', CONNECT_Command())
  command_processor.register_runner(server)
  
def test():
  from time import sleep
  server.listen('0.0.0.0', 12345)
  while True:
    server.run()
    c = server.accept()
    if c == 1:
      data = server.recv(0, 1024)
      server.send(1, data)
      server.run()
      sleep(3)
      server.run()
      print server.is_connected(0)
      print server.is_connected(1)
      sleep(3)
      server.close(0)
      server.close(1)

def test_client():
  from time import sleep
  i = server.connect('192.168.1.100', 5555)
  while server.is_connecting(i):
    server.run()
  if not server.is_connected(i):
    print "error"
    return
  print "connected"
  server.send(i, "test")
  server.run()
  server.close(i)
  server.run()

if __name__ == '__main__':
  test_client()
  
