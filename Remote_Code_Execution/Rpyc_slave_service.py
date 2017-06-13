"""
Server module class. If server is running and appropriate client sends code to the server,
proper function is being invoke.
"""
import rpyc
import ast
import os
import sys
import difflib

from rpyc.utils.server import ThreadedServer

"""
Default port on which server is running.
"""
PORT = 18861

"""
Directory where are being held received python codes from the clients.
"""
FILE_PATH = 'Received_codes'

"""
Path to file with saved python codes.
"""
DIRECTORY = None		

"""
Temporary file which is being used to save results of script.
"""
TMP_FILE = 'tmp.txt'


"""
Class MyService - main class of this module. 
When server start, proper directory designed for storing clients code has being create.
Codes from the clients, are being stored as long as session of the server lasts. 
When we run server again, files will be deleted.
"""
class MyService(rpyc.Service):

	"""
	Variable for storing code from the client.
	"""
	code = None
	
	"""
	Function which is invoke when new client will join to the server.
	Returns string message.
	"""
	def on_connect(self):
		print('Hello new client!')
		return('Succesfully connected to server!')
	pass
	
	"""
	Function which is invoke when client will close connection with a server.
	Returns string message.
	"""
	def on_disconnect(self):	
		print('Goodbye client!')
		return('Succesfully disconnected from server!')
	pass
		
	"""
	Function which is invoke from client perspective (exposed).
	Returns:
	True - if code is valid.
	False - if it is not.
	"""
	def exposed_send_and_check_code(self, code):	
		self.code = code
		if self.is_valid_python() == True:
			return True
		else:
			return False
	pass
	
	"""
	Function checks if received code can be compiled.
	
	Returns:
	True - if code can be compiled.
	False - if it is not. And throw exception.
	"""
	def is_valid_python(self):
		print('Code is: {}'.format(self.code))
		try:
			ast.parse(self.code)
		except SyntaxError:
			print('Code have errors')
			return False
		print('Code is valid')
		return True
	pass
	
	"""
	Function which is responsible for execution of code on the server side.
	Saves results to the temporary file, and sends results back to client, and after all file is being deleted.
	Returns string - result.
	"""
	def exposed_execute_code(self):
		result = ''
		exec(self.code)
		with open(TMP_FILE, 'r') as tmp_file:
			result = tmp_file.read()
		os.remove(TMP_FILE)
		return result
	pass
	
	"""
	Function stores codes received from clients in format like:
	conn[x], where x is a number of connection.
	In addition, checks if file with specified name is already existting.
	"""
	def store_code(self):
		file_name = self._conn._config["connid"] + '.txt'
		file_localization = os.path.join(DIRECTORY, file_name)
		if not os.path.exists(file_localization):
			with open(file_localization, 'w') as text_file:
				text_file.write(self.code)
		print('Succesfully saved the code!')
		self.code = None
	pass
	
	"""
	Function which is responsible for comparing code received from multiple clients.
	Saves results to the temporary file, and sends results back to client, and after all file is being deleted.
	Returns string (Full print like git diff) - result.
	"""
	def exposed_compare_codes(self):
		result = ''
		d = difflib.Differ()
		if os.listdir(DIRECTORY):
			for file in os.listdir(DIRECTORY):
				with open(os.path.join(DIRECTORY, file), 'r') as content_file:
					content = content_file.read()
					if content == self.code:
						result += 'Code same as in {}\n'.format(file)
					else:
						result += 'Differences with {}'.format(file)
						diff = d.compare(self.code.splitlines(), content.splitlines())
						result += '\n'.join(list(diff))
		self.store_code()
		return result
	pass
	
if __name__ == "__main__":
	
	DIRECTORY = os.path.join(os.getcwd(), FILE_PATH)
	if not os.path.exists(DIRECTORY): # if dir not exist, make new one
		os.makedirs(FILE_PATH)
	elif os.listdir(DIRECTORY): # if sth is in the dir
		filelist = [ f for f in os.listdir(DIRECTORY) ]
		for f in filelist:		# delete all in it
			os.remove(os.path.join(DIRECTORY, f))
	
	thread = ThreadedServer(MyService, port = PORT)
	thread.start()