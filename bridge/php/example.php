<?php
require("bridgeclient.class.php");

$client = new bridgeclient();

print("Assigning value to key D13\n");
$client->put("D13", "Test D13");

$test = $client->get("D13");
print("Value assigned to D13 is " . $test . "\n");

print("\n");

print("Assigning value to key D12\n");
$client->put("D12", "Test D12");

$test = $client->get("D12");
print("Value assigned to D12 is " . $test . "\n");

print("Deleting key D12\n");
$client->delete("D12");
$test = $client->get("D12");
print("Value assigned to D12 is " . $test . "\n");

print("\n");

print("Assigning value to key D11\n");
$client->put("D11", "Test D11");

$all = $client->getall();
print("Listing all stored values\n");
print_r($all);
print("Value assigned to D11 is " . $all->{"D11"} . "\n");

print("\n");

print("Sending mailbox message 'Hello world!'\n");
$client->mailbox("Hello world!");
?>
