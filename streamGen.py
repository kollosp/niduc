import numpy as np

class StreamGenerator:
	def __init__(self, length):
		self.len = length # how many bytes will be generated

	# generate new byte array
	def genRandom(self):
		#generate random bytes (string)	
		string = np.random.bytes(self.len)
		
		#rewrite string into byte array
		array = []
		for i in range(len(string)):
			array.append(ord(string[i]))
		return array
		