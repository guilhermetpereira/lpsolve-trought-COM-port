import serial
import time 
import lpsolve55

from config import ENABLE_PRINT
from config import COM_PORT
from config import BAUD_RATE

state = 'STATE_IDLE'

def wait_command():
	s = ser.read(1)
	if s == b'S':
		return True
	else:
		return False



if __name__ == "__main__":	
	ser = serial.Serial(COM_PORT, BAUD_RATE)

	if ser.is_open == False:
		if ENABLE_PRINT:
			print('Failed to open PORT')
		exit
	
	ser.flush()
	state = 'STATE_WAIT_COMMAND'

	while(1):
		if state == 'STATE_WAIT_COMMAND':
			if wait_command():
				state = 'STATE_RX_STORE'
			else:
				state = 'STATE_IDLE'
		elif state == 'STATE_RX_STORE':
			if ENABLE_PRINT:
				print(state)			
			state = 'STATE_IDLE'
		elif state == 'STATE_SOLVE_COOP':
			pass
		else: #STATE_IDLE
			pass
