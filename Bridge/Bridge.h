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

#ifndef BRIDGE_H_
#define BRIDGE_H_

#include <Arduino.h>
#include <Stream.h>

class BridgeClass: public Stream {
public:
  BridgeClass(Stream &_stream) : stream(_stream), currentHandle(0) {
  }

  void begin();
  unsigned int beginCommand(String command);
  void commandAddEscapedParam(String string);
  void endCommand();

  boolean commandIsRunning(unsigned int handle);

  unsigned int commandExitValue(unsigned int handle);
  
  void cleanCommand(unsigned int handle);
  
  unsigned long commandOutputSize(unsigned int handle);
  void readCommandOutput(unsigned int handle, unsigned int offset, 
                         unsigned int size, char *buffer);

  // Print methods
  size_t write(uint8_t c) { return stream.write(c); }
  size_t write(const uint8_t *buffer, size_t size) { 
    return stream.write(buffer, size);
  }

  // Stream methods
  int available() { return stream.available(); }
  int read() { return stream.read(); }
  int peek() { return stream.peek(); }
  void flush() { stream.flush(); }

private:
  static const char CTRL_C = 3;
  static const char PROMPT = '#';
  Stream &stream;
  unsigned int currentHandle;

  boolean wait();
  void dropAll();
};

// This subclass uses a serial port Stream
class SerialBridgeClass : public BridgeClass {
public:
  SerialBridgeClass(HardwareSerial &_serial)
      : BridgeClass(_serial), serial(_serial) {
  }
  
  void begin() {
    serial.begin(115200);
    BridgeClass::begin();
  }
  
private:
  HardwareSerial &serial;
};

extern SerialBridgeClass Bridge;

#endif /* BRIDGE_H_ */
