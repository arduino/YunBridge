/*
 * Curl.h
 *
 *  Created on: 11/apr/2013
 *      Author: federico
 */

#ifndef CURL_H_
#define CURL_H_

#include <Arduino.h>

class Curl {
public:
	Curl(BridgeClass &_bridge) :
			bridge(_bridge), handle(-1) {
	}

	String get(String url);
	void asyncGet(String url);

private:
	BridgeClass &bridge;
	unsigned int handle;

};

#endif /* CURL_H_ */
