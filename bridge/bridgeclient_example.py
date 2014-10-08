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

print 'Assigning value to key D12'
client.put('D12', 'Test D12')

test = client.get('D12')
print 'Value assigned to D12 is ' + test

print 'Deleting key D12'
client.delete('D12')
test = client.get('D12')
print 'Value assigned to D12 is ' + str(test)

print

print 'Assigning value to key D11'
client.put('D11', 'Test D11')

all = client.getall()
print 'Listing all stored values'
print all
print 'Value assigned to D11 is ' + all['D11']

print

print 'Using client.begin() and client.close() to speed up consecutive calls to Bridge'

client.begin()

for idx in range(1, 51):
  print 'Sending mailbox message \'Hello world ' + str(idx) + '!\''
  client.mailbox('Hello world ' + str(idx) + '!')

client.close()
