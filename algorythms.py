import numpy as np

def parityCode(array):
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

def crc16(data):
    '''
        CRC-16-ModBus Algorithm
    '''
    crc = 0xFFFF
    for b in data:
        crc ^= (0xFF & b)
        for _ in range(0, 8):
            if (crc & 0x0001):
                crc = ((crc >> 1) & 0xFFFF) ^ 0xA001
            else:
                crc = ((crc >> 1) & 0xFFFF)

    return [(crc&0xFF00)>>8 , crc&0xFF]

def crc8(data):
    '''
        CRC-8 Algorithm
    '''
    crc = 0xFF
    for b in data:
        crc ^= (0xFF & b)
        for _ in range(0, 8):
            if (crc & 0x01):
                crc = ((crc >> 1) & 0xFF) ^ 0xB2
            else:
                crc = ((crc >> 1) & 0xFF)

    return [crc&0xFF]