<?php
/*

Bridge Client PHP Class
------------------------
by Luca Soltoggio - 2013
http://www.arduinoelettronica.com/

Released under GPL v.2 license

Requirements
------------
In order to use this class you have to install php5, php5-mod-sockets, php5-mod-json and php5-cgi (or php5-cli)

Usage
-----
The usage is the same as bridgeclient.py
You have just two methods: get and put (see example.php)

*/

error_reporting(E_ERROR);

class bridgeclient {

	private $service_port = 5700;
	private $address = "127.0.0.1";
	private $socket;
	
	private function connect() {
		($this->socket = socket_create(AF_INET, SOCK_STREAM, SOL_TCP)) 
		|| die("socket_create() failed: " . socket_strerror(socket_last_error()) . "\n");
		socket_set_option($this->socket,SOL_SOCKET, SO_RCVTIMEO, array("sec"=>3, "usec"=>0));
		socket_connect($this->socket, $this->address, $this->service_port) 
		|| die("socket_connect() failed: " . socket_strerror(socket_last_error($this->socket)) . "\n");
	}
	
	private function disconnect() {
		socket_close($this->socket);
	}

	private function sendcommand($command,$key,$value="") {
		$jsonreceive = "";
		$obraces=0;
		$cbraces=0;

		$this->connect();
		
		$jsonsend = '{"command":"'.$command.'","key":"'.$key.'","value":"'.$value.'"}';
		socket_write($this->socket, $jsonsend, strlen($jsonsend));
	
		do {
		socket_recv($this->socket, $buffer, 1,0);
		$jsonreceive.=$buffer;
		if($buffer == "{") $obraces++;
		if($buffer == "}") $cbraces++;
		} while ($obraces != $cbraces);
		
		$this->disconnect();
		
		$jsonarray=json_decode($jsonreceive);
		if ($jsonarray->{'value'} == NULL) $jsonarray->{'value'}="None";
		
		return $jsonarray->{'value'};
	}
	
	public function get($key) {
		return $this->sendcommand("get",$key);
	}
	
	public function put($key,$value) {
		return $this->sendcommand("put",$key,$value);
	}

}
?>

