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

#################################
#  - selective repeat arq
# 
# frame:
#  - 
#
#
#
#################################

def codeParity(array):
	paritySum = 0

	#for all bytes
	for i in range(len(array)):
		#for all bits
		mask = 1
		for j in range(8):
			if (array[i] & mask) > 0:
				paritySum+=1
			
			mask *= 2

	return paritySum % 2 # 1 if odd

# return quality send-received/send
# stream - determinates how many bites can be transmited in time unit 
def testsParity(frameLen, swapProb, testCount): 
	
	sendBits = 0
	receivedBits = 0
	diffs = 0
	detectedMistakes = 0
	mistakes = 0

	carryover = testCount * 8 # 8 bits for every frame 


	for i in range(testCount):
		generator = StreamGenerator(frameLen)
		pipe = StreamPipe(swapProb)
		sendBytes = generator.genRandom() 
		sendBytes.append(codeParity(sendBytes) + ((2*i+1) & 0xFE))

		receivedBytes = pipe.transfer(sendBytes)
		
		parityCheck = receivedBytes.pop()
		receivedParity = codeParity(receivedBytes)
		
		if parityCheck&0x1 != (receivedParity&0x1):
			detectedMistakes += 1
			print 'incorrect' 
		
		receivedBytes.append(parityCheck)

		sendBits += len(sendBytes) * 8
		receivedBits += len(sendBytes)

		diff =  arrayDiff(sendBytes, receivedBytes)
		diffs+= diff

		if diff != 0:
			mistakes+=1


		#print('send: ')
		#displayByteArray(sendBytes)
		#print('received: ')
		#displayByteArray(receivedBytes)
		

		print('=============================')
		print('Test no: ' + str(i))
		print(' # generated ' + str(len(sendBytes) * 8) + ' bits')
		print(' # bit change probability: ' + str(swapProb))
		print(' # incorrect bits: '+ str(diff)+ ' (' + str(100*diff/(len(sendBytes) * 8)) + '%)')

	print('=============================')
	print('SUMMARY')
	print('Test count: '+str(testCount))
	print(' # generated ' + str(sendBits) + ' bits')
	print(' # carry-over ' + str(carryover) + ' bits (' + str(100*carryover/sendBits) + '%)')
	print(' # incorrect bits: '+ str(diffs)+ ' (' + str(100*diffs/sendBits) + '%)')
	print(' # incorrect frames: '+ str(mistakes) + ' (' + str(100*mistakes/testCount) + '%)')	
	if mistakes != 0:	
		print(' # detected as incorrect factor(detected/mistakes): '+ str(detectedMistakes) + ' (' + str(100*detectedMistakes/mistakes) + '%)')
	print(' # detected as incorrect factor(detected/send): '+ str(detectedMistakes) + ' (' + str(100*detectedMistakes/testCount) + '%)')		


if __name__ == "__main__":
	
	#params
	#############
	frameLen = 2 #bytes
	swapProb = 0.001
	testCount = 10000

	#############

	#run tests
	testsParity(frameLen, swapProb, testCount)

	'''
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
	'''


#11011001 11011110 10101001
#00000010

#00000000
