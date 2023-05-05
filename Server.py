from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from os.path import join, isdir
from os import getcwd, mkdir

class Server:
	__socket: socket
	__port = 2526
	__connections_map: dict[int, socket] = dict({})
	__num_connections = 0
	__files: list[str] = []
	__server_files: str

	def __init__(self, NUM_CLIENTS: int, PORT: int=None) -> None:
		'''
		# Params:
		NUM_CLIENTS - The number of clients that socket can listen for\n
		PORT (optional) - Default port number is 2526
		'''
		self.__socket = socket(AF_INET, SOCK_STREAM)

		if PORT != None:
			self.__port = PORT


		self.__server_files: str = join(getcwd(), "server_files")

		if isdir(self.__server_files) == False:
			mkdir(self.__server_files)

		self.__socket.bind(("", self.__port))
		self.__socket.listen(NUM_CLIENTS)
		thread = Thread(target=self.__listen, daemon=True)
		thread.start()
		thread.join()

	def __listen(self) -> None:
		'''
		A child thread that listens for new connections all the time
		'''
		while True:
			conn, addr = self.__socket.accept()
			self.__connections_map[self.__num_connections] = conn
			Thread(target=self.__recv).start()

	def __send_msg(self, connection_num: int, msg: str) -> None:
		self.__connections_map[connection_num].send(str(msg).encode())

	def __send_file(self, connection_num: int, file_path: str) -> None:
		'''
		Send the requested file to the client
		'''
		self.__connections_map[connection_num].send(open(join(self.__server_files, file_path), "r").read().encode())

	def __getFiles(self, connection_num: int) -> None:
		self.__send_msg(connection_num, self.__files)

	def __recv(self) -> None:
		'''
		A child thread that waits to recieve a message from a client
		'''
		CONNECTION_NUM: int = self.__num_connections
		self.__num_connections += 1

		while True:
			try:
				msg: str = \
					self.__connections_map[CONNECTION_NUM].recv(1024).decode()
			except:
				return

			if((msg == "--CLOSE--") or (msg == "")):
				try:
					self.close(CONNECTION_NUM)
				except:
					pass
				finally:
					return

			if msg == "--FILES--":
				self.__getFiles(CONNECTION_NUM)
				continue

			IDX = msg.rfind("FileName")
			if IDX > -1:
				self.__files.append(msg[:IDX])
				continue

			if "--END--" in msg:
				msg = msg[:msg.find("--END--")]
				open(join(self.__server_files, self.__files[-1]), "w").write(msg)
				continue

			if msg in self.__files:
				self.__send_file(CONNECTION_NUM, msg)
			else:
				self.__send_msg(CONNECTION_NUM, "--NON-Exists--")

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

if __name__ == "__main__":
	server = Server(1)