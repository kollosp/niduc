import streamGen
import algorythms

class Socket:
	def __init__(self, frameLen, frameToSend):
		self.frameLen = frameLen
		self.frameToSend = frameToSend
		
		# send frames. 
		self.frames = [None] * 127
		self.counter = 0 # maximum value is 127 as frames length
		self.globalCounter = 0 # counts all frames and indicates transmission end
							   # when grater or equal to frameToSend

	#index -1 means send next frame
	# checkSumFunction = function(sendBytes, counter) : sendBytesWithCrc 
	def sendFrame(self, checkSumFunction, index=-1):
		
		if(self.globalCounter >= self.frameToSend):
			return []

		if(index != -1):
			return self.resend(index)

		if(self.counter >= 127):
			self.counter = 0 
		
		#declare generator and create new data 
		
		generator = streamGen.StreamGenerator(self.frameLen)
		sendBytes = generator.genRandom() 


		#generate check sum and frame number
		sendBytes = checkSumFunction(sendBytes, self.counter)
		####################################

		#write to array (buffor for resend)
		self.frames[self.counter] = sendBytes
		self.counter+=1 
		self.globalCounter += 1
		return sendBytes

	def resend(self, index):
		if index < self.globalCounter and index < 127 and index > 0:
			return self.frames[index]
		return [0xFF]


	# function receive data
	# returns true if data has been transfered correctly
	# otherwise false 
	def receiveFrame(self, frame, checkSumFunction):

		[status, counter] = checkSumFunction(frame)

		return [status, counter]

	@staticmethod
	def parityAdder(sendBytes, counter):
		
		sendBytes.append(counter*2)
		sendBytes[len(sendBytes)-1] += algorythms.parityCode(sendBytes)
		return sendBytes

	# 0xFF if parity match if not 
	# counter to indicate which frame 
	# should be resend
	@staticmethod
	def checkParity(receivedBytes):
		
		#read frame number 
		counter = receivedBytes[len(receivedBytes)-1] >> 1 		
		
		#read parity bit
		p = receivedBytes[len(receivedBytes)-1] % 2
		
		#remove parity bit from data
		receivedBytes[len(receivedBytes)-1] = receivedBytes[len(receivedBytes)-1] - p

		#calc parity
		calculated = algorythms.parityCode(receivedBytes)

		#add parity bit to data
		receivedBytes[len(receivedBytes)-1] = receivedBytes[len(receivedBytes)-1] + p

		if p == calculated:
			return [True, counter]
		else: return [False, counter]

	@staticmethod
	def crc16Adder(sendBytes, counter):
		sendBytes.append(counter)
		crc = algorythms.crc16(sendBytes)
		sendBytes.append(crc[0])
		sendBytes.append(crc[1])
		return sendBytes

	@staticmethod
	def crc8Adder(sendBytes, counter):
		sendBytes.append(counter)
		crc = algorythms.crc8(sendBytes)
		sendBytes.append(crc[0])
		return sendBytes


	@staticmethod
	def checkCrc16(receivedBytes):
		crc = [0,0]
		counter = receivedBytes[-3] 
		crc[0] = receivedBytes[-2]
		crc[1] = receivedBytes[-1]		

		#print crc

		crcCalc = algorythms.crc16(receivedBytes[0:-2])

		#print crcCalc

		if crcCalc[0] == crc[0] and crcCalc[1] == crc[1]:
			return [True, counter]
		else: return [False, counter]

	@staticmethod
	def checkCrc8(receivedBytes):
		crc = [0]
		counter = receivedBytes[-2] 
		crc[0] = receivedBytes[-1]		

		#print crc

		crcCalc = algorythms.crc8(receivedBytes[0:-1])

		#print crcCalc

		if crcCalc[0] == crc[0]:
			return [True, counter]
		else: return [False, counter]
