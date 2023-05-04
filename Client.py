from socket import socket, AF_INET, SOCK_STREAM
from os.path import exists

class RequestRequired(Exception):
	pass

class Client:
	__socket: socket
	__port = 2526
	__is_connected = False
	__is_requested = False

	def __init__(self, IP_ADDR: str, PORT: int=None) -> None:
		'''
		# Params:
		IP_ADDR - The IP address of the server\n
		PORT (optional) - The port number of the server
		'''
		self.__socket = socket(AF_INET, SOCK_STREAM)

		if PORT != None:
			self.__port = PORT

		if self.__socket.connect_ex((IP_ADDR, self.__port)) == 0:
			self.__is_connected = True
		else:
			raise ConnectionError("Connection Failed")

	def send_file(self, file_path: str) -> None:
		'''
		Send a file from client machine to server

		# Params:
		file_path - The file path on the client to send to the server
		'''
		if exists(file_path):
			self.__socket.sendfile(file_path)
		else:
			FileNotFoundError("File not found")

	def requestFile(self, name_of_file: str) -> None:
		'''
		Request to download a file from the server to the client

		# Params:
		name_of_file - The path on the server to get a file
		'''
		self.__socket.send(name_of_file.encode())
		self.__is_requested = True

	def responce(self) -> str:
		'''
		Get the file that is returned from the server

		# Returns:
		A str that contains the content of the file. If the file does not
		exists then the string will be empty
		'''
		if self.__is_requested == True:
			self.__is_requested = False
			return self.__socket.recv(1024).decode()

		raise RequestRequired("A file request is required before ")

	def close(self) -> None:
		'''
		Closes the connection to the server. This will also set is_requested
		to False
		'''
		self.__is_connected = False
		self.__is_requested = False
		self.__socket.close()

	@property
	def is_connected(self) -> bool:
		'''
		# Returns:
		A bool that if True means that the client is connected to the server
		'''
		return self.__is_connected

	@property
	def is_requested(self) -> bool:
		'''
		# Returns:
		A bool that determins if a request for file has been sent to the
		server. This will be reset to false once responce has been called
		'''
		return self.__is_requested
