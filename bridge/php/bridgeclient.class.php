<?php
/*

Bridge Client PHP Class
------------------------
by Luca Soltoggio - 2013
http://www.arduinoelettronica.com/
by Federico Fissore - 2014
http://arduino.cc/

Released under GPL v.2 license

Requirements
------------
In order to use this class you have to install php5, php5-mod-sockets, php5-mod-json and php5-cgi (or php5-cli)

Usage
-----
The usage is the same as bridgeclient.py
You have methods: get, getall, put, delete, mailbox (see example.php)

*/

error_reporting(E_ERROR);

class bridgeclient {

	private $service_port = 5700;
	private $address = "127.0.0.1";
	private $socket;

	private function connect() {
		($this->socket = socket_create(AF_INET, SOCK_STREAM, SOL_TCP)) || die("socket_create() failed: " . socket_strerror(socket_last_error()) . "\n");
		socket_set_option($this->socket, SOL_SOCKET, SO_RCVTIMEO, array("sec" => 3, "usec" => 0));
		socket_connect($this->socket, $this->address, $this->service_port) || die("socket_connect() failed: " . socket_strerror(socket_last_error($this->socket)) . "\n");
	}

	private function disconnect() {
		socket_close($this->socket);
	}

	private function sendcommand($command, $key = "", $value = "", $data = "", $has_response = true) {
		$jsonreceive = "";
		$obraces = 0;
		$cbraces = 0;

		$this->connect();

		$jsonsend = new stdClass();
		$jsonsend->command = $command;
		if ($key <> "") {
			$jsonsend->key = $key;
		}
		if ($value <> "") {
			$jsonsend->value = $value;
		}
		if ($data <> "") {
			$jsonsend->data = $data;
		}
		$jsonsend = json_encode($jsonsend);

		socket_write($this->socket, $jsonsend, strlen($jsonsend));

		if (!$has_response) {
			return;
		}

		do {
			socket_recv($this->socket, $buffer, 1, 0);
			$jsonreceive .= $buffer;
			if ($buffer == "{") {
				$obraces++;
			}
			if ($buffer == "}") {
				$cbraces++;
			}
		} while ($obraces != $cbraces);

		$this->disconnect();

		$jsonarray = json_decode($jsonreceive);
		if ($jsonarray->{"value"} == NULL) {
			$jsonarray->{"value"} = "None";
		}

		return $jsonarray->{"value"};
	}

	public function get($key) {
		return $this->sendcommand("get", $key);
	}

	public function getall() {
		return $this->sendcommand("get");
	}

	public function put($key, $value) {
		return $this->sendcommand("put", $key, $value);
	}

	public function delete($key) {
		return $this->sendcommand("delete", $key);
	}

	public function mailbox($message) {
		return $this->sendcommand("raw", "", "", $message, false);
	}
}

?>
