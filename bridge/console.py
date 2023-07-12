##    This file is part of YunBridge.
##
##    YunBridge is free software; you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation; either version 2 of the License, or
##    (at your option) any later version.
##
##    This program is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License
##    along with this program; if not, write to the Free Software
##    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
##
##    As a special exception, you may use this file as part of a free software
##    library without restriction.  Specifically, if other files instantiate
##    templates or use macros or inline functions from this file, or you compile
##    this file and link it with other files to produce an executable, this
##    file does not by itself cause the resulting executable to be covered by
##    the GNU General Public License.  This exception does not however
##    invalidate any other reasons why the executable file might be covered by
##    the GNU General Public License.
##
##    Copyright 2013 Arduino LLC (http://www.arduino.cc/)

from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from select import select
import utils

class Console:
    def __init__(self, port=6571):
        # Create a server socket
        self.server = socket(AF_INET, SOCK_STREAM)
        self.server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        utils.try_bind(self.server, '127.0.0.1', port)
        self.server.listen(1)  # No connection backlog
        self.server.setblocking(0)
        
        # Initialize client-related data structures
        self.clients = []
        self.clients_sendbuffer = {}
        self.sockets = [self.server]
        
        # Initialize send and receive buffers
        self.sendbuffer = ''
        self.recvbuffer = ''
        
    def run(self):
        # Use select to check for available sockets
        sockets_to_read_from, _, _ = select(self.sockets, [], [], 0)
        
        # Accept new connections
        if self.server in sockets_to_read_from:
            self.accept()
            sockets_to_read_from.remove(self.server)
            
        # Read from sockets
        if len(self.sendbuffer) < 1024:
            for sock in sockets_to_read_from:
                self.socket_receive(sock)
        
        # Write buffers to sockets
        _, sockets_to_write_to, _ = select([], self.clients, [], 0)
        for client in sockets_to_write_to:
            try:
                buff = self.clients_sendbuffer[client]
                sent = client.send(buff)
                self.clients_sendbuffer[client] = buff[sent:]
            except:
                self.close(client)
        
        # Drop clients with large send buffers
        for client in self.clients:
            if len(self.clients_sendbuffer[client]) > 8192:
                self.close(client)
        
    def socket_receive(self, client):
        # Receive data from a client socket
        chunk = client.recv(1024)
        
        # Check if client socket closed
        if chunk == '':
            self.close(client)
            return None
        
        # Append received data to receive buffer
        self.recvbuffer += chunk
        
        # Send the received chunk as an echo to other clients
        for current_client in self.clients:
            if current_client != client:
                self.clients_sendbuffer[current_client] += chunk
    
    def write(self, data):
        # Send data to all connected clients
        for c in self.clients:
            self.clients_sendbuffer[c] += data
    
    def read(self, maxlen):
        # Read data from the receive buffer
        if maxlen > len(self.recvbuffer):
            res = self.recvbuffer
            self.recvbuffer = ''
        else:
            res = self.recvbuffer[:maxlen]
            self.recvbuffer = self.recvbuffer[maxlen:]
        return res
    
    def available(self):
        # Get the number of bytes available in the receive buffer
        return len(self.recvbuffer)
    
    def is_connected(self):
        # Check if there are connected clients
        return len(self.clients) > 0
    
    def accept(self):
        # Accept a new client connection
        client, address = self.server.accept()
        
        # Add the client to the list of connected clients
        self.sockets.append(client)
        self.clients.append(client)
        self.clients_sendbuffer[client] = ''
    
    def close(self, sock):
        # Close a client connection
        sock.close()
        
        # Remove the client from the list of connected clients
        self.clients.remove(sock)
        self.sockets.remove(sock)
        del self.clients_sendbuffer[sock]

console = Console()

class CommandRunner:
    def __init__(self, console):
        self.console = console
    
    def run(self, command, data):
        if command == 'P':
            # Write data to clients
            self.console.write(data)
            return ''
        elif command == 'p':
            # Read data from the console's receive buffer
            length = ord(data[0])
            return self.console.read(length)
        elif command == 'a':
            # Check if there are connected clients
            if self.console.is_connected():
                return '\x01'
            else:
                return '\x00'
        else:
            return ''

def test():
    # Create an instance of the CommandRunner class
    command_runner = CommandRunner(console)
    
    while True:
        # Run the console to process data
        console.run()
        
        # Prompt the user to enter a command
        command = input("Enter command: ")
        command = command.strip()
        
        # Execute the command using the CommandRunner instance
        if len(command) > 0:
            cmd = command[0]
            data = command[1:]
            result = command_runner.run(cmd, data)
            print("Result:", result)

if __name__ == '__main__':
    test()
