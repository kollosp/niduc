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

def test(frameLen, swapProb, framesCount, carryover, coderFunction, decoderFunction): 

	############
	# Statistics

	index = 0 # how many frames has been send
	dataIndex = 0 # how many frames of data (no repetes) has been send
	errors = 0 # how many broken frames has been received 
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
		[lastFrameStatus, lastFrameCounter] = s.receiveFrame(mixedFrame, s.checkParity)

		# check if detection algorythm do its job
		# error detected
		if helpers.arrayDiff(frame, mixedFrame):
			errors+=1

			# if error missed
			if lastFrameStatus == True:
				missedErrors+=1
		else:
			fullyCorrectedMessages+=1

		stdout.write("\r%d: progress: %d/%d (%d %%) miss/err: %d/%d correctMsg: %d" % (index, dataIndex,
		 framesCount, dataIndex*100/framesCount, missedErrors, errors, fullyCorrectedMessages))

	print '\n'
	print '---------------SUMMARY---------------'
	print ' # target(frames with data):          ', framesCount, 'frames', framesCount *(frameLen), 'bytes (data)'
	print ' # send:                              ', index, 'frames', index *(frameLen+carryover), 'bytes (data+carryover)'
	print ' # repeted:                           ', index - framesCount, 'frames', (index - framesCount)*(frameLen+carryover), 'bytes'  
	print ' #'
	print ' # correct received message:          ', fullyCorrectedMessages, 'frames', fullyCorrectedMessages*frameLen, 'bytes'
	print ' # lost messages (matched as correct):', framesCount - fullyCorrectedMessages,'frames', (framesCount - fullyCorrectedMessages)*frameLen, 'bytes' 
	print ' #'
	print ' # carryover:                         ', index, 'bytes.', (index - framesCount)*(frameLen+carryover), 'bytes of repeted frames' 
	print ' #'
	print ' # errors (frames):                   ', errors
	print ' # missed errors (frames):            ', missedErrors
	print ' # detected errors (frames):          ', errors - missedErrors


	#for i in range(10):
	#	helpers.displayByteArray(sender.sendFrame(sender.parityAdder))

def parityTest():
	#params
	#############
	frameLen = 1 #bytes
	swapProb = 0.001
	framesCount = 10000
	carryover = 1
	#############
	
	test(frameLen, swapProb, framesCount, carryover, socket.Socket.parityAdder, socket.Socket.checkParity)

	return


def crc16Test():
	#params
	#############
	frameLen = 2 #bytes
	swapProb = 0.001
	framesCount = 10000
	carryover = 3
	#############

	test(frameLen, swapProb, framesCount, carryover, socket.Socket.crc16Adder, socket.Socket.checkCrc16)

	return

if __name__ == "__main__":
	#parityTest()
	crc16Test()


	#array = [0x11, 0x03, 0x0, 0x6B, 0x0, 0x3] #crc 0x7687
	array = [0x11, 0x03, 0x06, 0xAE, 0x41, 0x56, 0x52, 0x43, 0x40] #crc 49AD 
	helpers.displayByteArray(algorythms.crc16(array))
	helpers.displayByteArray(array[0:-2])

	s = socket.Socket(10, 10)

	frame = s.sendFrame(s.crc16Adder)
	frame = s.sendFrame(s.crc16Adder)
	frame = s.sendFrame(s.crc16Adder)	
	helpers.displayByteArray(frame)
	#print algorythms.crc16(frame[0:-2])
	#frame[0]+=1
	helpers.displayByteArray(frame)
	
	#print algorythms.crc16(frame[0:-2])
	
	print s.receiveFrame(frame, s.checkCrc16)
