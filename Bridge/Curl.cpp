/*
 * Curl.cpp
 *
 *  Created on: 11/apr/2013
 *      Author: federico
 */

#include "Bridge.h"
#include "Curl.h"

String Curl::get(String url) {
	asyncGet(url);
	while (!bridge.hasResponse(handle)) {
	}
	return bridge.readString();
}

void Curl::asyncGet(String url) {
	bridge.beginCommand("curl");
	bridge.printEscaped(url);
	handle = bridge.endCommand();
}
