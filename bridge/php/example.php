<?php
require ("bridgeclient.class.php");

$client = new bridgeclient();

$client->put("D13","Test");

$test = $client->get("D13");
echo $test;

$all = $client->getall();
$all = json_decode($all, true);
print_r($all);
?>

