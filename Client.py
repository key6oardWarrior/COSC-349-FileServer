from socket import socket, AF_INET, SOCK_STREAM
from Options import Options

class RequestRequired(Exception):
	pass

class Client:
	__socket: socket
	__port = 2526
	__is_connected = False

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

	def send(self, option: Options) -> None:
		'''
		Send a message to the server

		# Params:
		option - What should the server do
		'''
		msg = "--FILES--" if option == Options.Files else "--CLOSE--"
		self.__socket.send(msg.encode())

	def send_file(self, file_path: str) -> None:
		'''
		Send a file from client machine to server.  Won't check if file exists

		# Params:
		file_path - The file path on the client to send to the server
		'''
		self.__socket.send((file_path[file_path.rfind("/")+1:] + "FileName").encode())
		self.__socket.send((open(file_path, "r").read() + "\n--END--").encode())

	def requestFile(self, name_of_file: str) -> None:
		'''
		Request to download a file from the server to the client

		# Params:
		name_of_file - The path on the server to get a file
		'''
		self.__socket.send(name_of_file.encode())

	def responce(self) -> str:
		'''
		Get the file that is returned from the server

		# Returns:
		A str that contains the content of the file. If the file does not
		exists then the string will be empty
		'''
		return self.__socket.recv(1024).decode()

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