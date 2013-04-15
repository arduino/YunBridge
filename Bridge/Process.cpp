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

#include <Process.h>

size_t ProcessStandardIO::write(uint8_t) {
}

int ProcessStandardIO::available() {
}

int ProcessStandardIO::read() {
}

int ProcessStandardIO::peek() {
}

void ProcessStandardIO::flush() {
}




void Process::begin(const char *command) {
	handle = bridge.beginCommand(command);
	IO.setHandle(handle);
}

void Process::addParameter(const char *param) {
	bridge.commandAddEscapedParam(param);
}

void Process::runAsynchronously() {
    bridge.endCommand();
}

boolean Process::running() {
	return bridge.commandIsRunning(handle);
}

unsigned int Process::exitValue() {
	return bridge.commandExitValue(handle);
}

unsigned int Process::run() {
	runAsynchronously();
	while (running())
		delay(100);
	return exitValue();
}

void Process::close() {
}

void Process::kill() {
}

