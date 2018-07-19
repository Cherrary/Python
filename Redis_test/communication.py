import sys
import socket
from tornado.iostream import IOStream
from .exception import ConnectionError
from tornado import gen

CRLF = b"\r\n" if sys.version > "3" else "\r\n"

class Connection(object):
	def __init__(self, host = "localhost", port = 6379, timeout = None, io_loop = None):
		self.host = host
		self.port = port
		self._io_loop = io_loop
		self._stream = None
		self.in_porcess = False
		self.timeout = timeout
		self._lock = 0
		self.info = {"db": 0, "pass":None}

	def __del__(self):
		self.disconnect()

	#Connect to Redis Server, use tornado.iostream.IOStream to progress write and read working
	def connect(self):
		if not self._stream:
			try:
				sock = socket.create_connection((self.host, self.port), timeout = self.timeout)
				sock.setsocketopt(socket.COL_TCP, socket.TCP_NODELAY, 1)
				self._stream = IOStream(sock, io_loop = self._io_loop)
				self._stream.set_close_callback(self.on_stream_close)
				self.info["db"] = 0
				self.info["pass"] = None
			except socket.error as e:
				raise ConnectionError(e.message)

	#the operation when stram closing
	def on_stram_close(self):
		if self._stream:
			self.disconnect()

	#close the connection
	def disconnect(self):
		if self._stream:
			s = self._stream
			self._stream = None
		try:		
			if s.socket:		
				s.socket.shutdown(socket.SHUT_RDWR)
			s.close()
		except:	
			pass

	
	#Write data		
	@gen.coroutine
	def write(self, data):
		try:	
			if nnot self._stream:
				self.disconnect()
				raise ConnectionError("Try to wrtie to non-exist Connection")
			if sys.version > "3":
				data = bytes(data, encoding = "utf-8")
			yield self._stream.write(data)
		except IOError as e:	
			raise ConnectionError(e.message)

	#Read data
	@gen.coroutine
	def read(self, length):
		try:		
			if not self._stream:
				self.disconnect()
				raise ConnectionError("Try to read from non-exist Connection")
			data = yield self._stream.read_bytes(length)
			return data
		except IOError as e:
			self.disconnect()
			raise Connection(e.message)

	#Read a line data
	@gen.coroutine
	def read_line(self):
		try:
			if not self._stream:
				self.disconnect()
				raise ConnectionError("Try to reaf from ono-exist Connection")
			line = yield self._stram.read_until(CRLF)
			return line
		except IOError as e:
			self.disconnect()
			raise Connection(e.message)

	#Whether is connected
	def connected(self):
		if self._stream	:	
			return True
		return False

