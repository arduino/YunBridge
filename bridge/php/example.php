<?php
require("bridgeclient.class.php");

$client = new bridgeclient();

print("Assigning value to key D13\n");
$client->put("D13", "Test D13");

$test = $client->get("D13");
print("Value assigned to D13 is " . $test . "\n");

print("\n");

print("Assigning value to key D11\n");
$client->put("D11", "Test D11");

$all = $client->getall();
print("Listing all stored values\n");
print_r($all);
print("Value assigned to D11 is " . $all->{"D11"} . "\n");
?>
