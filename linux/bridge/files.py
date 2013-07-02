
class Files:
  def __init__(self):
    self.files = { }
    self.next_id = 0
    
  def open(self, filename, mode):
    # Open a_file
    try:
      a_file = open(filename, mode)
    except IOError, e:
      return [e.errno, None]
    
    # Determine the next id to assign to a_file
    while self.next_id in self.files:
      self.next_id = (self.next_id + 1) % 256
    self.files[self.next_id] = a_file
    return [0, self.next_id]
    
  def close(self, file_id):
    if file_id not in self.files:
      return
    a_file = self.files[file_id]
    try:
      a_file.close()
    except:
      pass
    del self.files[file_id]
  
  def read(self, file_id, maxlen):
    if file_id not in self.files:
      return None
    a_file = self.files[file_id]
    try:
      return [0, a_file.read(maxlen)]
    except IOError, e:
      return [e.errno, None]

  def write(self, file_id, data):
    if file_id not in self.files:
      return None
    a_file = self.files[file_id]
    try:
      a_file.write(data)
      a_file.flush()
      return 0
    except IOError, e:
      return e.errno

  def seek(self, file_id, pos):
    if file_id not in self.files:
      return None
    a_file = self.files[file_id]
    try:
      a_file.seek(pos)
      return 0
    except IOError, e:
      return e.errno
    
  def tell(self, file_id):
    if file_id not in self.files:
      return [None, None]
    a_file = self.files[file_id]
    try:
      return [0, a_file.tell()]
    except IOError, e:
      return [e.errno, None]
      
files = Files()

class OPEN_Command:
  def run(self, data):
    [err, file_id] = files.open(data[1:], data[0]+'b')
    if err!=0:
      return chr(err) + chr(0)
    else:
      return chr(0) + chr(file_id)

class CLOSE_Command:
  def run(self, data):
    file_id = ord(data[0])
    files.close(file_id)
    return '\x00'
      
class READ_Command:
  def run(self, data):
    file_id = ord(data[0])
    maxlen = ord(data[1])
    [err, res] = files.read(file_id, maxlen)
    if err!=0:
      return chr(err)
    else:
      return chr(0) + res

class WRITE_Command:
  def run(self, data):
    file_id = ord(data[0])
    data = data[1:]
    err = files.write(file_id, data)
    return chr(err)
    
class SEEK_Command:
  def run(self, data):
    file_id = ord(data[0])
    pos =  ord(data[1]) << 24
    pos += ord(data[2]) << 16
    pos += ord(data[3]) << 8
    pos += ord(data[4])
    err = files.seek(file_id, pos)
    return chr(err)

class TELL_Command:
  def run(self, data):
    file_id = ord(data[0])
    [err, pos] = files.tell(file_id)
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
    
def init(command_processor):
  command_processor.register('F', OPEN_Command())
  command_processor.register('f', CLOSE_Command())
  command_processor.register('G', READ_Command())
  command_processor.register('g', WRITE_Command())
  command_processor.register('s', SEEK_Command())
  command_processor.register('S', TELL_Command())
  
