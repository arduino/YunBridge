#!/usr/bin/python

import sys

sys.path.insert(0, '/usr/lib/python2.7/bridge/')

from bridgeclient import BridgeClient as bridgeclient

client = bridgeclient()

print 'Assigning value to key D13'
client.put('D13', 'Test D13')

test = client.get('D13')
print 'Value assigned to D13 is ' + test

print

print 'Assigning value to key D11'
client.put('D11', 'Test D11')

all = client.getall()
print 'Listing all stored values'
print all
print 'Value assigned to D11 is ' + all['D11']
