#include <Process.h>

void brk() {
  Bridge.print((char)3);
}

void setup() {
  Bridge.begin();
  
  Process p;
  p.begin("curl");
  p.addParameter("http://arduino.cc/asciilogo.txt");
  int r = p.run();
  Bridge.print(r);brk();
}

void loop() {
}

