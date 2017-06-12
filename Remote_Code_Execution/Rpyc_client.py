"""
Client module. If server is avaiable, client sends code from python_code.txt and
is waiting for result from a server.
:param argv[1]: IP adress needed for connection.
"""
import rpyc
import sys
import time

"""
Default port which is necessary for connection with a server.
"""
PORT = 18861


"""
Getting first argument from command promt, and handling lack of it.
"""
try:
	arg = sys.argv[1]
except IndexError:
	print('Proper usage of script: python Rpyc_client.py IP_Address')
	sys.exit(1)
	
	
"""
Opening connection beetwen server and client using Rpyc library on PORT.
"""
conn = rpyc.connect(sys.argv[1], PORT)


"""
Opening file with example python code and invocation of function on a server.
Client is waiting for results from the server.
"""
code = open('python_code.txt', 'r')
if conn.root.send_and_check_code(code.read()) == True:
	print('Code can be compiled successfully!')
	print('Result of executing sent code:')
	print(conn.root.execute_code())
	print(conn.root.compare_codes())
	conn.close()
else:
	print('Errors in Code!')
code.close()


