from PySimpleGUI import Window, Text, Button, WIN_CLOSED, FileBrowse, Input, FolderBrowse
from sys import exit, argv
from os.path import exists, isfile, isdir, join

from Client import Client
from Options import Options

MAX_ARGC = 2
MIN_ARGC = 1
ARGC = len(argv)
if((ARGC < MIN_ARGC) or (ARGC > MAX_ARGC)):
	raise ValueError(f"Expected at least one command line argument, but {ARGC}")

window_name = "File Server Project"

def exit_app(event) -> bool:
	if((event == "Exit") or (event == WIN_CLOSED)):
		return True
	return False

def action() -> bool:
	layout = [
		[Button("Upload File"), Button("Download File")]
	]

	window = Window(window_name, layout)
	event, values = window.read()

	if exit_app(event):
		window.close()
		exit(0)

	window.close()
	return True if event == "Upload File" else False

def get_file(client: Client, layout: list[list]=[[]]) -> str:
	is_empty = 0 if len(layout[0]) == 0 else 1
	text_obj = [Text("Pick File to Upload"), FileBrowse()]

	if is_empty:
		layout.append(text_obj)
	else:
		layout[is_empty].extend(text_obj)

	layout.append([Button("Submit")])

	win = Window(window_name, layout)
	event, value = win.read()
	win.close()

	if exit_app(event):
		client.close()
		exit(0)

	return value["Browse"]

server_ip_addr = argv[1]
try:
	client = Client(server_ip_addr)
except ConnectionError:
	Window(window_name, [[Text("Connection Failed")]]).read()
	exit(0)

def getFileLayout():
	return \
	[
		[Text(files[1:-1])],
		[Text("Enter which file you want to download"), Input(key="file"), Button("Submit")]
	]

while True:
	if action():
		# if user wants to upload file
		is_exists = True
		file_path: str = ""
		arg: list[list] = [[]]

		while is_exists:
			file_path: str = get_file(client, arg)
			arg = [[]]

			if isfile(file_path) == False:
				arg[0] = [Text("The file selected is not a file", text_color="red")]

			if exists(file_path) == False:
				arg[0] = [Text("File selected does not exist", text_color="red")]

			if len(arg[0]) == 0:
				is_exists = False

		client.send_file(file_path)

	else: # user wants to download file
		client.send(Options.Files)
		files: str = client.responce().strip()

		if files == "[]":
			layout = [
				[Text("There are no files to download")]
			]
		else:
			layout = getFileLayout()

		SIZE = len(layout)
		win = Window(window_name, layout)

		while True:
			event, values = win.read()

			if exit_app(event):
				client.close()
				exit(0)

			values["file"] = values["file"].strip()

			if values["file"] in files:
				client.requestFile(values["file"])
				break
			else:
				layout = getFileLayout().append([Text("That file is not in the server")])
				win.close()
				win = Window(window_name, layout)

		win.close()

		while True:
			win = Window(window_name, [[Text("Enter where to download"), FolderBrowse(), Input("Enter name of file", key="name"), Button("Submit")]])
			event, values = win.read()

			if exit_app(event):
				exit(0)

			values["Browse"] = values["Browse"].strip()
			values["name"] = values["name"].strip()

			if isdir(values["Browse"]) == False:
				win.close()
				continue

			open(join(values["Browse"], values["name"]), "w").write(client.responce())
			win.close()
			break
