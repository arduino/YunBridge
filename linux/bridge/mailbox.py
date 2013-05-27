
from tcp import TCPJSONServer
from collections import deque

json = TCPJSONServer('127.0.0.1', 5700)

class Mailbox:
  def __init__(self):
    self.incoming = deque()
    self.data_store = { }

  def run(self):
    json.run()
    if json.available()>0:
      try:
        self.ext_command(json.read())
      except:
        pass

  def ext_command(self, msg):
    if not 'command' in msg:
      return
    command = msg['command']

    if command=='raw':
      self.incoming.append(msg['data'])
      return

    if command=='get':
      k = msg['key']
      v = self.data_store_get(k)
      json.write({ 'response' : 'get', 'key' : k, 'value' : v })
      return

    if command=='put':
      k = msg['key']
      v = msg['value']
      self.data_store_put(k, v)
      json.write({ 'response' : 'put', 'key' : k, 'value' : v })
      return

  def data_store_put(self, k, v):
    self.data_store[k] = v
    
  def data_store_get(self, k):
    if k in self.data_store:
      return self.data_store[k]
    else:
      return None
      
  def send(self, data):
    json.write({ 'request' : 'raw', 'data' : data })
    
  def recv(self):
    if len(self.incoming)>0:
      return self.incoming.popleft()
    return None
            
  def peek(self):
    if len(self.incoming)>0:
      return self.incoming[0]
    else:
      return None
    
mailbox = Mailbox()

class SEND_Command:
  def run(self, data):
    mailbox.send(data)
    return ""

class RECV_Command:
  def run(self, data):
    msg = mailbox.recv()
    if msg is None:
      return ""
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
      return ""
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
  command_processor.register('m', RECV_Command())
  command_processor.register('n', AVAILABLE_Command())
  command_processor.register('D', DATASTORE_PUT_Command())
  command_processor.register('d', DATASTORE_GET_Command())
  command_processor.register_runner(mailbox)

