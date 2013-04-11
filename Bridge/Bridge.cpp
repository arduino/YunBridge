/*
 * Bridge.cpp
 *
 *  Created on: 11/apr/2013
 *      Author: federico
 */

#include "Bridge.h"

void BridgeClass::begin() {
	print(CTRL_C);
	print(F("\n"));
	delay(500);
	flush();
}

boolean BridgeClass::wait() {
	int start = millis();
	while (read() != PROMPT) {
		if ((millis() - start) > 5000) {
			return false;
		}
	}
	return true;
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

unsigned int BridgeClass::endCommand() {
	print(F(" &\n"));
	wait();
	return currentHandle;
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
