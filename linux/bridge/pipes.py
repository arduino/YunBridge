
class Pipe:
  def __init__(self):
    self.incoming = [ ]
    self.outgoing = [ ]

  def send(self, data):
    self.outgoing.append(data)
    
  def recv(self):
    if len(self.incoming)>0:
      return self.incoming.pop(0)
    return None
            
  def available(self):
    return len(self.incoming)
    
pipe = Pipe()

class SEND_Command:
  def __init__(self, pipe):
    self.pipe = pipe

  def run(self, data):
    self.pipe.send(data)
    return ""

class RECV_Command:
  def __init__(self, pipe):
    self.pipe = pipe

  def run(self):
    data = self.pipe.recv()
    if data is None:
      return ""
    else:
      return data

class AVAILABLE_Command:
  def __init__(self, pipe):
    self.pipe = pipe

  def run(self):
    res = self.pipe.available()
    if res>32:
      return chr(32)
    else:
      return chr(res)
    
def init(command_processor):
  command_processor.register('P', SEND_Command(pipe))
  command_processor.register('p', RECV_Command(pipe))
  command_processor.register('a', AVAILABLE_Command(pipe))
  
