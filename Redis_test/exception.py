class RedisError(Exception):
	pass

class ConnectionError(RedisError):
	pass

class ResponseError(RedisError):
 	pass
