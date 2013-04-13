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

boolean BridgeClass::wait() {
	int start = millis();
	while ((millis() - start) < 5000) {
		if (read() == PROMPT) {
			return true;
		}
	}
	return false;
}

unsigned int BridgeClass::beginCommand(String command) {
	print(F("arduino-launch "));
	print(currentHandle);
	print(F(" "));
	print(command);
	print(F(" "));
	return currentHandle++;
}

void BridgeClass::printEscaped(String param) {
	// TODO: handle " ' ! $ & > and other special chars in string
	print(F(" \""));
	print(param);
	print(F("\""));
}

void BridgeClass::endCommand() {
	print(F(" &\n"));
	wait();
}

void BridgeClass::dropAll() {
	while (available() > 0) {
		read();
	}
}

boolean BridgeClass::hasResponse(unsigned int handle) {
	print(F("arduino-has-output "));
	print(handle);
	String output = readStringUntil('\n');
	wait();
	return output.equals("0");
}

String BridgeClass::beginRead(unsigned int handle, unsigned int offset,
		unsigned int size) {
	print(F("arduino-read-output "));
	print(handle);
	print(F(" "));
	print(offset);
	print(F(" "));
	print(size);
	print(F(" "));
	String output = readStringUntil('\n');
	wait();
	return output;
}
