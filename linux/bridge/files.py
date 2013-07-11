
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
  
