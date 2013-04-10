



class BridgeClass {
public:
  BridgeClass(Stream &_wrt) : 
  wrt(_wrt), nextHandle(0) {  
  }

  void begin();

  void beginWrite(String cmd);
  void writeInt(int);
  void writeString(String);
  unsigned int endWrite();

  int available();
  int available(unsigned int handle);

  String beginRead();
  String beginRead(unsigned int handle);
  //int readIntParam();
  //String readStringParam(int len, boolean next=true);
  void endRead();

private:
  void flush();
  boolean wait();

private:
  static const char CTRL_C = 3;

  unsigned int nextHandle;
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

void BridgeClass::flush() {
  while (wrt.available())
    wrt.read();
}

boolean BridgeClass::wait() {
  int start = millis();
  while (wrt.read()!='#')
    if ((millis() - start) > 5000)
      return false;
  return true;
}

int BridgeClass::available() {
}

int BridgeClass::available(unsigned int handle) {
}

void BridgeClass::beginWrite(String cmd) {
  wrt.print(F("arduino-launch "));
  wrt.print(nextHandle);
  wrt.print(F(" "));
  wrt.print(cmd);
}

void BridgeClass::writeInt(int value) {
  wrt.print(F(" "));
  wrt.print(value);
}

void BridgeClass::writeString(String string) {
  // TODO: handle " ' ! $ & > and other special chars in string
  wrt.print(F(" \""));
  wrt.print(string);
  wrt.print(F("\""));
}

unsigned int BridgeClass::endWrite() {
  wrt.println(F(" &"));
  wait();
  return nextHandle++;
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
    bridge.beginWrite("CURL");
    bridge.writeString(url);
    handle = bridge.endWrite();
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






