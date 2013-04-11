/*
 * Bridge.h
 *
 *  Created on: 11/apr/2013
 *      Author: federico
 */

#ifndef BRIDGE_H_
#define BRIDGE_H_

#include <Arduino.h>
#include <Stream.h>

class BridgeClass: public Stream {
public:
	BridgeClass(Stream &_stream) :
			currentHandle(0), stream(_stream) {
	}

	void begin();

	unsigned int beginCommand(String command);
	unsigned int endCommand();
	void printEscaped(String string);

	boolean hasResponse(unsigned int handle);

	String beginRead(unsigned int handle, unsigned int offset,
			unsigned int size);
	//int readIntParam();
	//String readStringParam(int len, boolean next=true);
	void endRead();

	// Print methods
	size_t write(uint8_t c) {
		return stream.write(c);
	}
	size_t write(const uint8_t *buffer, size_t size) {
		return stream.write(buffer, size);
	}

	// Stream methods
	int available() {
		return stream.available();
	}
	int read() {
		return stream.read();
	}
	int peek() {
		return stream.peek();
	}
	void flush() {
		stream.flush();
	}

private:
	static const char CTRL_C = 3;
	static const char PROMPT = '#';
	Stream &stream;
	unsigned int currentHandle;

	boolean wait();
	void dropAll();
};

#endif /* BRIDGE_H_ */
