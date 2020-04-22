import socket
import select
from time import gmtime, strftime

server_socket = socket.socket()
server_socket.bind(('0.0.0.0', 8000))
server_socket.listen(5)
open_client_sockets = []
messages_to_send = []
client_names_list = []
client_names_left_list = []
client_names_kicked_list = []
silenced_names_list = []
private_messages_list = []
meneger_names_list = ['Daniel Vazana', 'd']


def send_waiting_messages(wait_list):
	"""The function sends messages to clients in case a client wanted to send a message to the group or to inform the
	 clients that a client left or should inform clients that the client has been bounced or sent private messages """
	time = strftime("%H:%M", gmtime())
	for message in messages_to_send:
		(client_socket, data_to_send) = message
		sent = False
		for socket_to_send in wait_list:
			if socket_to_send is not client_socket and (
					not get_name_by_socket(client_socket).replace('@', '') in silenced_names_list):
				socket_to_send.send(
					str(time + ' ' + get_name_by_socket(client_socket) + ' : ' + data_to_send).replace('\n', ''))
				sent = True
		if not sent and client_socket in wait_list and (
				not get_name_by_socket(client_socket).replace('@', '') in silenced_names_list):
			client_socket.send('Server : Your message was not sent because there are no clients who can accept it')
		elif not sent and client_socket in wait_list and \
				get_name_by_socket(client_socket).replace('@', '') in silenced_names_list:
			client_socket.send('Server : Your message was not sent because you are muted')
		messages_to_send.remove(message)
	for name_quit in client_names_left_list:
		for socket_to_send in wait_list:
			socket_to_send.send(str(time + ' ' + name_quit + ' has left the chat!').replace('\n', ''))
		client_names_left_list.remove(name_quit)
	for name_kicked in client_names_kicked_list:
		for socket_to_send in wait_list:
			socket_to_send.send(str(time + ' ' + name_kicked + ' has been kicked from the chat!').replace('\n', ''))
		get_socket_by_name(name_kicked).send('leave - sever command')
		client_names_kicked_list.remove(name_kicked)
		client_names_list.remove(get_tuple_by_name(name_kicked))
	for tuple_to_send in private_messages_list:
		if tuple_to_send[2] == 'Enter another name: ':
			tuple_to_send[0].send(tuple_to_send[2])
		elif tuple_to_send[2] == str(meneger_names_list):
			tuple_to_send[0].send(time + " " + tuple_to_send[2])
		elif tuple_to_send[1] in wait_list and (not get_name_by_socket(tuple_to_send[0]) in silenced_names_list):
			tuple_to_send[1].send(time + ' !' + get_name_by_socket(tuple_to_send[0]) + ' : ' + tuple_to_send[2])
		elif tuple_to_send[1] in wait_list and get_name_by_socket(tuple_to_send[0]) in silenced_names_list and \
				tuple_to_send[0] in wait_list:
			tuple_to_send[0].send('Server : Your message was not sent because you are muted')
		private_messages_list.remove(tuple_to_send)


def in_the_client_names_list(socket_to_find):
	"""Checks if the client in list of my clients names(socket and name each client) by his socket"""
	flag = False
	for current_tuple in client_names_list:
		if socket_to_find in current_tuple:
			flag = True
	return flag


def get_name_by_socket(socket_to_find):
	"""Get name from my clients list(socket and name each client) by his socket"""
	for current_tuple in client_names_list:
		if socket_to_find in current_tuple:
			if current_tuple[1] in meneger_names_list:
				return '@' + current_tuple[1]
			else:
				return current_tuple[1]


def get_socket_by_name(name):
	"""Get socket from my clients list(socket and name each client) by his name"""
	for current_tuple in client_names_list:
		if name in current_tuple:
			return current_tuple[0]


def in_the_client_names_list_by_name(name):
	"""Checks if the client in list of my clients names(socket and name each client) by his name"""
	flag = False
	for current_tuple in client_names_list:
		if name in current_tuple:
			flag = True
	return flag


def get_tuple_by_name(name):
	"""Get tuple(item) from my clients list(socket and name each client) by his name"""
	for current_tuple in client_names_list:
		if name in current_tuple:
			return current_tuple


while True:
	rlist, wlist, xlist = select.select([server_socket] + open_client_sockets, open_client_sockets, [])
	for current_socket in rlist:
		if current_socket is server_socket:
			(new_socket, address) = server_socket.accept()
			open_client_sockets.append(new_socket)
			print 'Client connected'
		else:
			print 'Getting data'
			data = current_socket.recv(1024).replace('\n', '')
			if data == '':
				client_names_left_list.append(get_name_by_socket(current_socket))
				open_client_sockets.remove(current_socket)
				print "Connection with client closed."
			else:
				if '!' == data[0] and ':' in data and in_the_client_names_list_by_name(
						data[data.find('!') + 1: data.find(':')]):
					tuple_to = (current_socket, get_socket_by_name(data[data.find('!') + 1: data.find(':')]),
								data[data.find(':') + 1:])
					private_messages_list.append(tuple_to)
				elif 'view-managers' in data:
					private_messages_list.append((current_socket, current_socket, str(meneger_names_list)))
				elif 'mute' in data:
					if in_the_client_names_list_by_name(data.replace('mute ', '')) and get_name_by_socket(
							current_socket).replace('@', '') in meneger_names_list:
						silenced_names_list.append(data.replace('mute ', ''))
				elif 'make-manager' in data:
					if in_the_client_names_list_by_name(data.replace('make-manager ', '')) and get_name_by_socket(
							current_socket).replace('@', '') in meneger_names_list:
						meneger_names_list.append(data.replace('make-manager ', ''))
				elif 'quit' in data:
					print 'Removing client'
					if get_name_by_socket(current_socket) is not None:
						client_names_left_list.append(get_name_by_socket(current_socket))
					if in_the_client_names_list(current_socket):
						client_names_list.remove(get_tuple_by_name(get_name_by_socket(current_socket).replace('@', '')))
					open_client_sockets.remove(current_socket)
				elif 'kick' in data:
					if in_the_client_names_list_by_name(data.replace('kick ', '')) and get_name_by_socket(
							current_socket).replace('@', '') in meneger_names_list:
						print 'Kicking client'
						client_names_kicked_list.append(data.replace('kick ', ''))
						open_client_sockets.remove(get_socket_by_name(data.replace('kick ', '')))
				elif get_name_by_socket(current_socket) is None and not in_the_client_names_list_by_name(data):
					print 'Appendding name'
					client_names_list.append((current_socket, data.replace('@', '')))
				elif get_name_by_socket(current_socket) is None and in_the_client_names_list_by_name(data):
					print 'Asking new name'
					private_messages_list.append((current_socket, current_socket, 'Enter another name: '))
				else:
					print 'Appendding message'
					messages_to_send.append((current_socket, data))

	send_waiting_messages(wlist)
