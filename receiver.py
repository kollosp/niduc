import helpers as helpers
import numpy as np

class Receiver: 
	def __init__(self):
		self.framesReceived = 0 # counts how many frames receiver has received

	# function receive data from sender and return 
	# true if 
	def receive(self, frame):
		return