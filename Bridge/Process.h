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

#ifndef PROCESS_H_
#define PROCESS_H_

#include <Bridge.h>

class ProcessStandardIO : public Stream {
public:
  ProcessStandardIO() { }
  size_t write(uint8_t);
  int available();
  int read();
  int peek();
  void flush();

  void setHandle(unsigned int h) { handle = h; }
private:
  unsigned int handle;
};

class Process {
public:
  // Default constructor uses global Bridge instance
  Process() : bridge(Bridge) { }
  // Constructor with a user provided BridgeClass instance
  Process(BridgeClass &_bridge) : bridge(_bridge) { }
  
  void begin(const char *command);
  void addParameter(const char *param);
  unsigned int run();
  void runAsynchronously();
  boolean running();
  unsigned int exitValue();
  void close();
  void kill();
  
private:
  BridgeClass &bridge;
  ProcessStandardIO IO;
  unsigned int handle;
};

#endif
