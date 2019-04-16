from sys import stdout

#display byte array in hex format 0xXX
def displayByteArray(array):
	for x in array:
		stdout.write("0x%02X " % x)
	print ''

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