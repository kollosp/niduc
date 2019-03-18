import numpy as np
from sys import stdout

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
	
#display byte array in hex format 0xXX
def displayByteArray(array):
	for x in array:
		stdout.write("0x%02X " % x)
	print '\n'

#how many bits have been changed
def arrayDiff(a1, a2):
	if len(a1) != len(a2): 
		print "a1 and a2 must be the same length"	
	
	diff = 0
	for i in range(len(a1)):
		mask = 1
		for j in range(8):
			if (a1[i] & mask) != (a2[i] & mask):
				diff+=1
			mask*=2
	return diff




#################################
#
# TO DO:
#  - add sending multiple frames
#    in one test
#  - coder (function or class)
#  - decoder (function or class) 
#  - add retransmission requests 
#
# Algorythm:
# - generate random bytes
# - code them using coder
# - send via pipe
# - received and decode
# - calc diffs
#
#################################








if __name__ == "__main__":
	
	#params
	#############
	frameLen = 10 #bytes
	swapProb = 0.1

	#############

	bitsSend = frameLen * 8 # calc bits count 

	generator = StreamGenerator(frameLen)
	pipe = StreamPipe(swapProb)

	sendBytes = generator.genRandom() 
	
	
	receivedBytes = pipe.transfer(sendBytes)
	print('=============================')
	print('send: ')
	displayByteArray(sendBytes)
	print('received: ')
	displayByteArray(receivedBytes)
	
	diff =  arrayDiff(sendBytes, receivedBytes)

	print('=============================')
	print(' # generated ' + str(bitsSend) + ' bits')
	print(' # bit change probability: ' + str(swapProb))
	print(' # changed detected: '+ str(diff)+ ' (' + str(100*diff/bitsSend) + '%)')
