import numpy as np

class StreamPipe:
	def __init__(self, prob):
		self.prob = prob

	def transfer(self, array):
		ret = []
		
		#for all bytes
		for i in array:
			#for all bits
			mask = 1
			value = 0
			for j in range(8):
				if np.random.rand() <= self.prob:
	 
					#swap bit value
					if (i & mask) == 0:
						value += mask 
				else:
					value += (i & mask)
				#mask shift
				mask *= 2

			#append to returned array
			ret.append(value)
		
		return ret