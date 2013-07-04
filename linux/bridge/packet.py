
import tty, termios, select
from contextlib import contextmanager
from sys import stdin, stdout
from subprocess import call

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
    while len(data) > 0:
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
    #if self.result != crc:
    #  print 'CRC:' + hex(self.result) + '!' + hex(crc)
    return self.result == crc
    
    

def send(index, msg):
  crc = CRC(stdout)
  crc.write('\xff')        # Packet start
  crc.write(chr(index))    # Message No. inside Pipe
  l = len(msg)
  crc.write(chr(l >> 8))   # Message length
  crc.write(chr(l & 0xFF)) # Message length
  crc.write(msg)           # Payload
  crc.write_crc()          # CRC
  stdout.flush()


class RESET_Command:
  def __init__(self, reader):
    self.reader = reader
    
  def run(self, data):
    if data[0] != 'X':
      call(['/usr/bin/blink-start', '100'])
      return chr(1)
    if data[1:4] != '100':
      call(['/usr/bin/blink-start', '100'])
      return chr(2)
    call(['/usr/bin/blink-stop'])
    return chr(0)
    
class PacketReader:
  def __init__(self, processor):
    self.index = 999
    self.last_response = None
    self.processor = processor
    self.processor.register('X', RESET_Command(self))
      
  # Timed read
  def t_read(self):
    ret = select.select([stdin.fileno()], [], [], 0.050)
    if ret[0] == [stdin.fileno()]:
      return stdin.read(1)
    return None
    
  def process(self):
    # Do a round of runners
    self.processor.run()
    
    # Wait for Start Of Packet
    while True:
      c = self.t_read()
      if c is None:
        return None
      if ord(c) == 0xFF:
        break
          
    # Read index and len
    index = self.t_read()
    if index is None:
      return None
    len_hi = self.t_read()
    if len_hi is None:
      return None
    len_lo = self.t_read()
    if len_lo is None:
      return None
      
    crc = CRC(None)
    crc.write(c)
    crc.write(index)
    crc.write(len_hi)
    crc.write(len_lo)
      
    len_t = (ord(len_hi) << 8) + ord(len_lo)
    
    # Read payload
    data = ''
    for x in range(len_t):
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
    if len(data) == 5 and data[0:2] == 'XX':
      self.index = ord(index)
     
    # Check for out-of-order packets
    if self.index != ord(index):
      if not self.last_response is None:
        send(ord(index), self.last_response)
      return True
      
    # Process command
    result = self.processor.process(data)
    
    # Send Acknowledge
    send(self.index, result)
    self.index = (self.index + 1) & 0xFF
    self.last_response = result
    return True
      
    

