/*
  Copyright (c) 2013 Arduino LLC. All right reserved.

  This library is free software; you can redistribute it and/or
  modify it under the terms of the GNU Lesser General Public
  License as published by the Free Software Foundation; either
  version 2.1 of the License, or (at your option) any later version.

  This library is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
  Lesser General Public License for more details.

  You should have received a copy of the GNU Lesser General Public
  License along with this library; if not, write to the Free Software
  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA
*/

#include "Bridge.h"

void BridgeClass::begin() {
  print(CTRL_C);
  print(F("\n"));
  delay(500);
  // Wait for OpenWRT message
  // "Press enter to activate console"
  dropAll();
  
  print(F("\n"));
  delay(400);
  dropAll();

  print(F("cd /\n"));
  wait();
  print(F("arduino-begin\n"));
  wait();
  print(F("cd /arduino\n"));
  wait();
}

unsigned int BridgeClass::beginCommand(String command) {
  print(F("arduino-launch "));
  print(currentHandle);
  print(F(" "));
  print(command);
  print(F(" "));
  return currentHandle++;
}

void BridgeClass::commandAddEscapedParam(String param) {
  // TODO: handle " ' ! $ & > and other special chars in string
  print(F(" \""));
  print(param);
  print(F("\""));
}

void BridgeClass::endCommand() {
  print(F(" &\n"));
  wait();
}

boolean BridgeClass::commandIsRunning(unsigned int handle) {
  print(F("find processes/"));
  print(handle);
  print(F(" -name running|wc -l\n"));
  find("\n");
  boolean running = (parseInt() == 1);
  wait();
  return running;
}

unsigned int BridgeClass::commandExitValue(unsigned int handle) {
  print(F("cat processes/"));
  print(handle);
  print(F("/result\n"));
  find("\n");
  int result = parseInt();
  wait();
  return result;
}

void BridgeClass::cleanCommand(unsigned int handle) {
  print(F("arduino-consume "));
  print(handle);
  print('\n');
  wait();
}

unsigned long BridgeClass::commandOutputSize(unsigned int handle) {
  print(F("arduino-read-size "));
  print(handle);
  print(F(" stdout\n"));
  find("\n");
  long res = parseInt();
  wait();
  return res;
}

void BridgeClass::readCommandOutput(unsigned int handle, unsigned int offset, 
    unsigned int size, uint8_t *buffer) {
  print(F("arduino-read "));
  print(handle);
  print(' ');
  print(offset);
  print(' ');
  print(size);
  print(F(" stdout\n"));
  find("\n");
  readBytes(reinterpret_cast<char *>(buffer), size);
  wait();
}

boolean BridgeClass::wait() {
  /*
  int start = millis();
  while ((millis() - start) < 5000) {
    if (read() == PROMPT) {
      return true;
    }
  }
  return false;
  */
  find("arduino# ");
}

void BridgeClass::dropAll() {
  while (available() > 0) {
    read();
  }
}

// Bridge instance
#ifdef __AVR_ATmega32U4__
  // Leonardo variants (where HardwareSerial is Serial1)
  SerialBridgeClass Bridge(Serial1);
#else
  SerialBridgeClass Bridge(Serial);
#endif
