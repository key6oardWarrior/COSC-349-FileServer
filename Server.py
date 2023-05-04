from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from os.path import exists

class Server:
	__socket: socket
	__port = 2526
	__connections_map: dict[int, socket] = dict({})
	__num_connections = 0

	def __init__(self, NUM_CLIENTS: int, PORT: int=None) -> None:
		'''
		# Params:
		NUM_CLIENTS - The number of clients that socket can listen for\n
		PORT (optional) - Default port number is 2526
		'''
		self.__socket = socket(AF_INET, SOCK_STREAM)

		if PORT != None:
			self.__port = PORT

		self.__socket.bind(("", self.__port))
		self.__socket.listen(NUM_CLIENTS)
		Thread(target=self.__listen, daemon=True).start()

	def __listen(self) -> None:
		'''
		A child thread that listens for new connections all the time
		'''
		while True:
			conn, addr = self.__socket.accept()
			self.__connections_map[self.__num_connections] = conn

			Thread(target=self.__recv, daemon=True).start()
			self.__num_connections += 1

	def __send_msg(self, connection_num: int, msg: str) -> None:
		self.__connections_map[connection_num].send(msg)

	def __send_file(self, connection_num: int, file_path: str) -> None:
		'''
		Send the requested file to the client
		'''
		self.__connections_map[connection_num].sendfile(file_path)

	def __recv(self) -> None:
		'''
		A child thread that waits to recieve a message from a client
		'''
		CONNECTION_NUM: int = self.__num_connections

		while True:
			msg: str = self.__connections_map[CONNECTION_NUM].recv(1024).decode()
			msg = msg.strip()

			if msg == "CLOSE":
				self.close(CONNECTION_NUM)
				return

			if exists(msg):
				self.__send_file(CONNECTION_NUM, msg)
			else:
				self.__send_msg(CONNECTION_NUM, "That file does not exist")

	def close(self, connection_num: int) -> None:
		'''
		Close a connection

		# Params:
		connection_num - Which connection to close
		'''
		self.__connections_map.pop(connection_num).close()

	def close_all(self) -> None:
		'''
		Close all connections to the server
		'''
		for key in self.__connections_map:
			self.__connections_map.pop(key).close()

		self.__socket.close()