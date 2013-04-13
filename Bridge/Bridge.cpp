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

// Remove warnings
#define printF(x) \
	{ prog_char ___str[] PROGMEM = x; \
	print(___str); }
	
void BridgeClass::begin() {
	print(CTRL_C);
	printF("\n");
	delay(500);
	// Wait for OpenWRT message
	// "Press enter to activate console"
	dropAll();
	
	printF("\n");
	delay(400);
	dropAll();

	printF("cd /\n");
	wait();
	printF("arduino-begin\n");
	wait();
	printF("cd /arduino\n");
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
	printF("arduino-launch ");
	print(currentHandle);
	printF(" ");
	print(command);
	printF(" ");
	return currentHandle++;
}

void BridgeClass::printEscaped(String param) {
	// TODO: handle " ' ! $ & > and other special chars in string
	printF(" \"");
	print(param);
	printF("\"");
}

unsigned int BridgeClass::endCommand() {
	printF(" &\n");
	wait();
	return currentHandle;
}

void BridgeClass::dropAll() {
	while (available() > 0) {
		read();
	}
}

boolean BridgeClass::hasResponse(unsigned int handle) {
	printF("arduino-has-output ");
	print(handle);
	String output = readStringUntil('\n');
	wait();
	return output.equals("0");
}

String BridgeClass::beginRead(unsigned int handle, unsigned int offset,
		unsigned int size) {
	printF("arduino-read-output ");
	print(handle);
	printF(" ");
	print(offset);
	printF(" ");
	print(size);
	printF(" ");
	String output = readStringUntil('\n');
	wait();
	return output;
}
