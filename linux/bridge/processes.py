
from subprocess import Popen, PIPE

from fcntl import fcntl, F_SETFL
from os import O_NONBLOCK


class Processes:
  def __init__(self):
    self.processes = { }
    self.next_id = 0
    
  def create(self, cmd):
    # Start the background process
    try:
      proc = Popen(cmd, stdout=PIPE, stderr=PIPE, stdin=PIPE)
      fcntl(proc.stdout.fileno(), F_SETFL, O_NONBLOCK)
      fcntl(proc.stderr.fileno(), F_SETFL, O_NONBLOCK)
      proc.buffered_out = ''
      proc.buffered_err = ''
    except OSError, e:
      return None
    
    # Determine the next id to assign to process
    while self.next_id in self.processes:
      self.next_id = (self.next_id + 1) % 256
    self.processes[self.next_id] = proc
    return self.next_id
    
  def is_running(self, proc_id):
    if proc_id not in self.processes:
      return False
    proc = self.processes[proc_id]
    if proc.poll() is None:
      return True
    else:
      return False
      
  def wait(self, proc_id):
    if proc_id not in self.processes:
      return None
    proc = self.processes[proc_id]
    return proc.wait()
    
  def clean(self, proc_id):
    if proc_id not in self.processes:
      return
    proc = self.processes[proc_id]
    if proc.poll() is None:
      try:
        proc.kill()
      except OSError:
        # Trap: [Errno 3] No such process
        pass
    del self.processes[proc_id]
  
  def try_buffer_output(self, proc):
    if len(proc.buffered_out) < 32: 
      try:
        proc.buffered_out += proc.stdout.read(32)
      except IOError:
        # Traps: [Errno 11] Resource temporarily unavailable
        pass
      
  def read_output(self, proc_id, maxlen):
    if proc_id not in self.processes:
      return None
    proc = self.processes[proc_id]
    self.try_buffer_output(proc)
    if len(proc.buffered_out) < maxlen:
      res = proc.buffered_out
      proc.buffered_out = ''
    else:
      res = proc.buffered_out[0:maxlen]
      proc.buffered_out = proc.buffered_out[maxlen:]
    return res

  def available_output(self, proc_id):
    if proc_id not in self.processes:
      return None
    proc = self.processes[proc_id]
    self.try_buffer_output(proc)
    return len(proc.buffered_out)
               
  def write_input(self, proc_id, data):
    if proc_id not in self.processes:
      return
    proc = self.processes[proc_id]
    proc.stdin.write(data)
    proc.stdin.flush()
    
processes = Processes()

class RUN_Command:
  def __init__(self, processes):
    self.proc = processes

  def run(self, data):
    proc_id = self.proc.create(data.split('\xFE'))
    if proc_id is None:
      return chr(1) + chr(0)
    return chr(0) + chr(proc_id)

class RUNNING_Command:
  def __init__(self, processes):
    self.proc = processes
  
  def run(self, data):
    proc_id = ord(data[0])
    res = self.proc.is_running(proc_id)
    if res:
      return '\x01'
    else:
      return '\x00'
      
class WAIT_Command:
  def __init__(self, processes):
    self.proc = processes
  
  def run(self, data):
    proc_id = ord(data[0])
    res = self.proc.wait(proc_id)
    if res is None:
      res = 0
    return chr((res >> 8) & 0xFF) + chr(res & 0xFF)

class CLEAN_UP_Command:
  def __init__(self, processes):
    self.proc = processes
  
  def run(self, data):
    proc_id = ord(data[0])
    self.proc.clean(proc_id)
    return ''

class READ_OUTPUT_Command:
  def __init__(self, processes):
    self.proc = processes
  
  def run(self, data):
    proc_id = ord(data[0])
    maxlen = ord(data[1])
    res = self.proc.read_output(proc_id, maxlen)
    if res is None:
      return ''
    return res

class AVAILABLE_OUTPUT_Command:
  def __init__(self, processes):
    self.proc = processes
  
  def run(self, data):
    proc_id = ord(data[0])
    avail = self.proc.available_output(proc_id)
    if avail is None:
      avail = 0
    return chr(avail)

class WRITE_INPUT_Command:
  def __init__(self, processes):
    self.proc = processes
  
  def run(self, data):
    proc_id = ord(data[0])
    data = data[1:]
    self.proc.write_input(proc_id, data)
    return ''

def init(command_processor):
  command_processor.register('R', RUN_Command(processes))
  command_processor.register('r', RUNNING_Command(processes))
  command_processor.register('W', WAIT_Command(processes))
  command_processor.register('w', CLEAN_UP_Command(processes))
  command_processor.register('O', READ_OUTPUT_Command(processes))
  command_processor.register('o', AVAILABLE_OUTPUT_Command(processes))
  command_processor.register('I', WRITE_INPUT_Command(processes))
  
