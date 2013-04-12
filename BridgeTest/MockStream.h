/*
 * MockStream.h
 *
 *  Created on: 12/apr/2013
 *      Author: federico
 */

#ifndef MOCKSTREAM_H_
#define MOCKSTREAM_H_

#include <Arduino.h>
#include <Stream.h>

class MockStream: public Stream {

public:

	MockStream() {

	}

	// Print methods
	size_t write(uint8_t c) {
		Serial.print(c);
		//printf("%d", c);
	}

	size_t write(const uint8_t *buffer, size_t size) {
		Serial.print(size);
		//printf("%d %d", buffer, size);
	}

	// Stream methods
	int available() {
		return 0;
	}
	int read() {
		return -1;
	}
	int peek() {
		return -1;
	}
	void flush() {
	}
};

#endif /* MOCKSTREAM_H_ */
