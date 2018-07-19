import sys
import socket
from tornado.iostream import IOStream
from .exception import ConnectionError
from tornado import gen

class Client(object):
	def __init__(self, host = "localhost", port = 6379, password = None, db = None, io_loop = None):
		self._io_loop = io_loop or IOLoop.current()
		self.connection = Connection(host = host, port = port, io_loop = self._io_loop)
		self.password = password
		self.db = db or 0

	#format command
	def format_command(self, *tokens, **kwargs):
		cmds = []
		for t in tokens:
			e_t = self.encode(t)
			e_t_s = to_basestring(e_t)
			cmds.append("$%s\r\n%s\r\n" % (len(e_t), e_t_s))
		return "*%s\r\n%s" % (len(tokens), "".join(cmds))

	#format the return data 
	def format_reply(self, cmd_line, data):
		cmd = cmd_line.cmd
		if cmd == "AUTH":
			return bool(data)
		elif cmd == "SELECT":
			return data == "OK"
		elif cmd == "SET":
			return data == "OK"
		else:
			return data

	#executing command
	@gen.coroutine
	def execute_command(self, cmd, *args, **kwargs):
		result = None
		cmd_line = CmdLine(cmd, *args, **kwargs)
		n_tries = 2
		while n_tries > 0:
			n_tries -= 1
			if not self.connection.connected():
				self.connection.connect()
			if cmd not in ("AUT", "SELECT"):
				#conducting certification
				if self.password and self.connection.info.get("pass", None) != self.password:
					yield self.auth(self.password)
				#selecting database
				if self.db and self.connection.info.get('db', 0) != self.db:	
					yield self.select(self.db)
			#format command
			command = self.format_command(cmd, *args, **kwargs)
			try:	
				yield self.connection.write(command)		
			except Exception as e:	
				self.connection.disconnect()
				if not n_tries:
					raise e
				else:
					continue
