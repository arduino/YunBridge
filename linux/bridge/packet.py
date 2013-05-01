
import tty, termios, select
from contextlib import contextmanager
from sys import stdin, stdout

@contextmanager
def cbreak():
    old_attrs = termios.tcgetattr(stdin)
    tty.setcbreak(stdin)
    tty.setraw(stdin)
    try:
        yield
    finally:
        termios.tcsetattr(stdin, termios.TCSADRAIN, old_attrs)

class CRC:
  def __init__(self, file):
    self.result = 0xAAAA
    self.file = file
    
  def write(self, data):
    while len(data)>0:
      if not self.file is None:
        self.file.write(data[0])
      self.result = self.result ^ ord(data[0])
      self.result = (self.result >> 8) + ((self.result & 0xFF) << 8)
      data = data[1:]
      
  def write_crc(self):
    #print hex(self.result)
    stdout.write(chr(self.result >> 8))
    stdout.write(chr(self.result & 0xFF))
  
  def check(self, crc):
    if self.result != crc:
      print "CRC:" + hex(self.result) + "!" + hex(crc)
    return self.result == crc
    
    

def send(index, msg):
  crc = CRC(stdout)
  crc.write("\xff")        # Packet start
  crc.write(chr(index))    # Message No. inside Pipe
  crc.write(chr(len(msg))) # Message length
  crc.write(msg)           # Payload
  crc.write_crc()          # CRC
  stdout.flush()


  
class PacketReader:
  def __init__(self, processor):
    self.index = 0
    self.last_response = None
    self.processor = processor
    
  # Timed read
  def t_read(self):
    ret = select.select([stdin.fileno()], [], [], 0.050)
    if ret[0] == [stdin.fileno()]:
      return stdin.read(1)
    return None
    
  def process(self):
    # Wait for Start Of Packet
    while True:
      c = self.t_read()
      if c is None:
        return None
      if ord(c)==0xFF:
        break
          
    # Read index and len
    index = self.t_read()
    if index is None:
      return None
    len = self.t_read()
    if len is None:
      return None
        
    crc = CRC(None)
    crc.write(c)
    crc.write(index)
    crc.write(len)
      
    # Read payload
    data = ""
    for x in range(ord(len)):
      c = self.t_read()
      if c is None:
        return None
      data += c
      crc.write(c)
    
    # Read and check CRC
    crc_hi = self.t_read()
    if crc_hi is None:
      return None
    crc_lo = self.t_read()
    if crc_lo is None:
      return None
      
    crc_hi = ord(crc_hi)
    crc_lo = ord(crc_lo)
    if not crc.check((crc_hi << 8) + crc_lo):
      return None
    
    # Check for reset command
    if data=='XX':
      self.index = ord(index)
     
    # Check for out-of-order packets
    if self.index > ord(index):
      send(ord(index), self.last_response)
      return True
      
    # Process command
    result = self.processor.process(data)
    
    # Send Acknowledge
    send(self.index, result)
    self.index = (self.index + 1) & 0xFF
    self.last_response = result
    return True
      
    

