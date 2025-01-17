import numpy as np
import helpers
import receiver
import socket 
import algorythms
import streamGen
import streamPipe as streamPipe
from sys import stdout






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
		generator = streamGen.StreamGenerator(frameLen)
		pipe = streamPipe.StreamPipe(swapProb)
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

		diff = helpers.arrayDiff(sendBytes, receivedBytes)
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

def test(frameLen, swapProb, framesCount, carryover, coderFunction, decoderFunction, simpleOutput = False): 

	############
	# Statistics

	index = 0 # how many frames has been send
	dataIndex = 0 # how many frames of data (no repetes) has been send
	errors = 0 # how many broken frames has been received 
	errorsBits = 0 # how many broken bits has been received 
	missedErrors = 0 # how many bed frames has been marked as correct
	fullyCorrectedMessages = 0

	############

	pipe = streamPipe.StreamPipe(swapProb)
	s = socket.Socket(frameLen, framesCount)
	frame = []
	lastFrameStatus = 0
	lastFrameCounter = 0

	while True:
		index+=1 

		#generate frames
		if lastFrameStatus == True:
			frame = s.sendFrame(coderFunction)	
			dataIndex+=1
		else: 
			# resending
			frame = s.sendFrame(decoderFunction, lastFrameCounter)
			# if frame is [0xFF] it means that lastFrameStatus has invalid value
			if len(frame) == 1 and frame[0] == 0xFF:
				lastFrameStatus = True
				continue

		#if there is no more frames
		if len(frame) == 0:
			break
		
		# transfer
		mixedFrame = pipe.transfer(frame)
		
		# detect if frame has been correctly send
		# if last frame status != 0 then ask for repeate
		[lastFrameStatus, lastFrameCounter] = s.receiveFrame(mixedFrame, decoderFunction)

		# check if detection algorythm do its job
		# error detected
		missedBits = helpers.arrayDiff(frame, mixedFrame) 
		if missedBits:
			errorsBits+=missedBits
			errors += 1

			# if error missed
			if lastFrameStatus == True:
				missedErrors+=1
		else:
			fullyCorrectedMessages+=1

		stdout.write("\r%d: progress: %d/%d (%d %%) miss/err: %d/%d correctMsg: %d" % (index, dataIndex,
		 framesCount, dataIndex*100/framesCount, missedErrors, errors, fullyCorrectedMessages))

	carryoverTargetPlusRepeted = (index - framesCount)*(frameLen+carryover) + framesCount *(carryover)	

	if simpleOutput == False:


		print '\n'
		print '---------------SUMMARY---------------'
		print ' # target(frames with data):          ', framesCount, 'frames', framesCount *(frameLen), 'bytes (data)'
		print ' # target(carryover):                 ', framesCount *(carryover), 'bytes', (carryover)*100/(frameLen+carryover), '% (carryover)/(data+carryover)'
		print ' # send:                              ', index, 'frames', index *(frameLen+carryover), 'bytes (data+carryover)'
		print ' # send(repeted):                     ', index - framesCount, 'frames', (index - framesCount)*(frameLen+carryover), 'bytes'  
		print ' # send(carryover):                   ', index - framesCount, 'frames', (index - framesCount)*(frameLen+carryover), 'bytes'  
		print ' #'
		print ' # correct received message:          ', fullyCorrectedMessages, 'frames', fullyCorrectedMessages*frameLen, 'bytes'
		print ' # lost messages (matched as correct):', framesCount - fullyCorrectedMessages,'frames', (framesCount - fullyCorrectedMessages)*frameLen, 'bytes' 
		print ' #'
		print ' # carryover:                         ', index - framesCount, 'frames', (index - framesCount)*(frameLen+carryover), 'bytes of repeted frames' 
		print ' # carryover(target + repeted)        ', carryoverTargetPlusRepeted, 'bytes,', carryoverTargetPlusRepeted*100 / (framesCount *(frameLen)+carryoverTargetPlusRepeted), '%'
		print ' # errors (frames):                   ', errors
		print ' # errors (bits):                     ', errorsBits
		print ' # missed errors (frames):            ', missedErrors
		print ' # detected errors (frames):          ', errors - missedErrors

	else:
		print '\n'
		print '---------------SUMMARY---------------'
		print 'alpha: ', 100 - carryoverTargetPlusRepeted*100 / (framesCount *(frameLen)+carryoverTargetPlusRepeted)
		print 'frame len: ', frameLen

	#for i in range(10):
	#	helpers.displayByteArray(sender.sendFrame(sender.parityAdder))

def parityTest(frameLen, swapProb, framesCount, simpleOutput):
	#params
	#############
	carryover = 1
	#############

	print "---------parity---------" 
	test(frameLen, swapProb, framesCount, carryover, socket.Socket.parityAdder, socket.Socket.checkParity, simpleOutput)

	return


def crc16Test(frameLen, swapProb, framesCount, simpleOutput):
	#params
	#############
	carryover = 3
	#############

	print "---------crc16---------" 
	test(frameLen, swapProb, framesCount, carryover, socket.Socket.crc16Adder, socket.Socket.checkCrc16, simpleOutput)

	return

def crc8Test(frameLen, swapProb, framesCount, simpleOutput):
	#params
	#############
	carryover = 2
	#############

	print "---------crc8---------" 
	test(frameLen, swapProb, framesCount, carryover, socket.Socket.crc8Adder, socket.Socket.checkCrc8, simpleOutput)

	return

def createTest(frameLen, swapProb, framesCount, algorythm,simpleOutput):
	
	if algorythm == 1:
		parityTest(frameLen, swapProb, framesCount, simpleOutput)
	elif algorythm == 8:
		crc8Test(frameLen, swapProb, framesCount, simpleOutput)
	elif algorythm == 16: 
		crc16Test(frameLen, swapProb, framesCount, simpleOutput)

def main():
	#parityTest()

	# Function generates test.
	frameLen = 30	
	swapProb = 0.001
	framesCount = 1000
	algorythm = 1
	simpleOutput = False
	createTest(frameLen, swapProb, framesCount, algorythm, simpleOutput)

	return 

	'''
	#array = [0x11, 0x03, 0x0, 0x6B, 0x0, 0x3] #crc 0x7687
	array = [0x11, 0x03, 0x06, 0xAE, 0x41, 0x56, 0x52, 0x43, 0x40] #crc 49AD 
	helpers.displayByteArray(algorythms.crc8(array))
	helpers.displayByteArray(array[0:-1])

	s = socket.Socket(10, 10)

	frame = s.sendFrame(s.crc8Adder)
	frame = s.sendFrame(s.crc8Adder)
	helpers.displayByteArray(frame)
	frame = s.sendFrame(s.crc8Adder)	
	#print algorythms.crc16(frame[0:-2])
	#frame[0]+=1
	helpers.displayByteArray(frame)
	
	#print algorythms.crc16(frame[0:-2])
	
	print s.receiveFrame(frame, s.checkCrc8)
	'''


if __name__ == "__main__":
	main()