import shelve
import logging

logger = logging.getLogger(__name__)

# shelve.open("users.dat")
# shelve.sync()
# shelve.close()

class Storer:
	def __init__(self, filename):
		self.filename = filename
	
	def save(self, key, value):
		s = shelve.open(self.filename)
		s[key] = value
		s.close()
		logger.info("Save object '%s' in db" % key)

	def read(self, key):
		s = shelve.open(self.filename)
		if s.has_key(key):
			logger.info("Succesful read object '%s' from db" % key)
			obj = s[key]
			s.close()
			return obj
		else:
			logger.info("Object '%s' missing in db" % key)
		s.close()
		return None
	