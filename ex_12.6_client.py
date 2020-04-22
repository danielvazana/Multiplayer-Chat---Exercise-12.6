import socket
import select
import sys

client_socket = socket.socket()
client_socket.connect(('127.0.0.1', 8000))
client_socket.setblocking(True)
open_client_sockets = [client_socket]

print """
The commands you have:
- view-managers
- quit
- kick + name : (only if you are manager)
- make-manager + name : (only if you are manager)
- mute + name : (only if you are manager)
- ! + name + : + message (private message)
Enter your name: """
run = True
while run:
	ready = select.select([client_socket], [], [], 0.5)
	if ready[0]:
		server_data = client_socket.recv(1024)
		if 'leave - sever command' in server_data:  # Checks if we have been kicked out 
			run = False
		else:
			print server_data
	if run and sys.stdin in select.select([sys.stdin], [], [], 0)[0]:  # Checks if keyboard is pressed
		line = sys.stdin.readline()
		if line:
			if 'quit' in line:
				client_socket.send('quit')
				client_socket.close()
				run = False
			else:
				print 'Input: ' + line
				client_socket.send(line)
