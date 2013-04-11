



class BridgeClass : 
public Stream {
public:
  BridgeClass(Stream &_wrt) : 
  wrt(_wrt) {  
  }

  void begin();

  void beginCommand();
  unsigned int endCommand();

  int available(unsigned int handle);

  String beginRead();
  String beginRead(unsigned int handle);
  //int readIntParam();
  //String readStringParam(int len, boolean next=true);
  void endRead();

  void printEscaped(String string);

  // Print methods
  size_t write(uint8_t c) { 
    return wrt.write(c); 
  }
  size_t write(const uint8_t *buffer, size_t size) { 
    return wrt.write(buffer, size); 
  }

  // Stream methods
  int available() { 
    return wrt.available(); 
  }
  int read() { 
    return wrt.read(); 
  }
  int peek() { 
    return wrt.peek(); 
  }
  void flush() { 
    wrt.flush(); 
  }

private:
  boolean wait();
  void dropAll();

private:
  static const char CTRL_C = 3;
  Stream &wrt;
};


void BridgeClass::begin() {
  wrt.print(CTRL_C);
  wrt.print(F("\n"));
  delay(500);
  flush();

  wrt.print(F("cd /\n"));
  wait();
  wrt.print(F("arduino-begin\n"));
  wait();
  wrt.print(F("cd /arduino\n"));
  wait();
}

boolean BridgeClass::wait() {
  int start = millis();
  while (wrt.read()!='#')
    if ((millis() - start) > 5000)
      return false;
  return true;
}

int BridgeClass::available(unsigned int handle) {
}

void BridgeClass::beginCommand() {
  print(F("arduino-launch "));
}

void BridgeClass::printEscaped(String string) {
  // TODO: handle " ' ! $ & > and other special chars in string
  print(F(" \""));
  print(string);
  print(F("\""));
}

unsigned int BridgeClass::endCommand() {
  wrt.println(F(" &"));
  wait();
  return ;
}

void BridgeClass::dropAll() {
  while (available()>0)
    read();
}


class BridgeCurl {
public:
  BridgeCurl(BridgeClass &_bridge) : 
  bridge(_bridge) {
  }

  String get(String url) {
    asyncGet(url);
    while (!available())
      ;
    return read();
  }

  void asyncGet(String url) {
    bridge.beginCommand();
    bridge.printEscaped(url);
    handle = bridge.endCommand();
  }

  int available() {
    return bridge.available(handle);
  }

  String read() {
  }

private:
  BridgeClass &bridge;
  int handle;
};




BridgeClass Bridge(Serial);

BridgeCurl Curl(Bridge);

void setup() {
  Serial.begin(115200);
  Bridge.begin();
}

void loop() {
  //Curl.get("http://bug.st/");
}










