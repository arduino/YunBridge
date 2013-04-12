/*
 * Bridge_test.cpp
 *
 *  Created on: 12/apr/2013
 *      Author: federico
 */

#include <Bridge.h>
#include "MockStream.h"

void setup() {
  Serial.begin(115200);
  while(!Serial);
  
  MockStream* ms = new MockStream();
  BridgeClass* bridge = new BridgeClass((Stream&) ms);
  Serial.print(bridge->available());
}

// the loop routine runs over and over again forever:
void loop() {
}

