import serial
import time 
import lpsolve55
from dataclasses import dataclass



from config import ENABLE_PRINT
from config import COM_PORT
from config import BAUD_RATE

state = 'STATE_IDLE'
buffer = []
nodes_list = []

@dataclass
class Node:
	assigned_ts : int
	energy : int
	bitmap :[]


def wait_command():
	
	s = ser.read(1)
	
	if s == b'S':
		return True
	else:
		return False

def read_serial():
	s = ser.read(1)
	while s != b'T':
		buffer.append(s)
		s = ser.read(1)
	ser.flushInput()
	ser.flushOutput()



def process_data():
	nodes_list.clear()
	total_nodes = int(buffer.pop(0))
	while len(buffer) != 0  and buffer[0] != b'F':
		if buffer[0] == b'N':
			buffer.pop(0)
			assigned_ts = int(''.join(buffer.pop(0).decode('utf-8')),16)
			
			energy_str = [x.decode('utf-8') for x in buffer[0:8]]
			energy_int = int(''.join(energy_str),16)
			del buffer[0:8]
			bitmap = []
			for byte in range(-(total_nodes // -8)): # essa locura no range é só um ceil
				value = int(''.join(buffer.pop(0).decode('utf-8')),16)
				for bit in range(7):
					if (bool((0x01 << bit) & value)): 
						bitmap.append(bit)
			nodes_list.append(Node(assigned_ts,energy_int,bitmap))
	buffer.clear()



if __name__ == "__main__":	
	ser = serial.Serial(COM_PORT, BAUD_RATE)

	if ser.is_open == False:
		if ENABLE_PRINT:
			print('Failed to open PORT')
		exit
	
	ser.flushInput()
	ser.flushOutput()
	state = 'STATE_WAIT_COMMAND'

	while(1):

		if state == 'STATE_WAIT_COMMAND':
			if wait_command():
				start_time = time.time()
				read_serial()
				process_data()
				print("--- %s seconds ---" % (time.time() - start_time))
				if ENABLE_PRINT:
					print(nodes_list)	
					pass		
				state = 'STATE_WAIT_COMMAND'
				# state = 'STATE_RX_STORE'
			else:
				state = 'STATE_IDLE'

		elif state == 'STATE_SOLVE_COOP':
			pass
		else: #STATE_IDLE
			pass
