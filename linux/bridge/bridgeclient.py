
from tcp import TCPJSONClient
from time import sleep

class BridgeClient:
  def wait_response(self, json, timeout):
    while timeout>=0:
      r = json.recv()
      if not r is None:
        return r
      timeout -= 0.1
      sleep(0.1)
    return None

  def wait_key(self, key, json, timeout):
    while True:
      r = self.wait_response(json, timeout)
      if r is None:
        return None
      try:
        if r['key'] == key:
          return r['value']
      except:
        pass

  def get(self, key):
    json = TCPJSONClient('127.0.0.1', 5700)
    json.send({'command':'get', 'key':key})
    r = self.wait_key(key, json, 10)
    json.close()
    return r

  def put(self, key, value):
    json = TCPJSONClient('127.0.0.1', 5700)
    json.send({'command':'put', 'key':key, 'value':value})
    r = self.wait_key(key, json, 10)
    json.close()
    return r

