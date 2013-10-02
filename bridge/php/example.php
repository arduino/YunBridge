<?php
require ("bridgeclient.class.php");

$client = new bridgeclient();

$client->put("D13","Test");
$test= $client->get("D13");
echo $test;
?>

