try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup


setup(name = "redis_test", version = "0.1", description = "Asynchronous Redis client for the Tournado Web Server", author = "Cherrary", author_email = "xc20160917@163.com", license="http://www.apache.org/licenses/LICENSE-2.0",keywords = ["Redis", "Tornado"])
