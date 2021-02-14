import serial
import time 
import lpsolve55
import os
import numpy as np
from dataclasses import dataclass



from config import ENABLE_PRINT
from config import COM_PORT
from config import BAUD_RATE
from config import ENERGY_CONST

state = 'STATE_IDLE'
buffer = []
nodes_list = []

@dataclass
class Node:
	assigned_ts : int
	energy : int
	bitmap : []


def wait_command():
	ser.reset_input_buffer()
	ser.reset_output_buffer()
	s = ser.read(1)
	counter = 0
	while s == b'S':
		counter = counter +1
		s = ser.read(1)
	if counter!=4:
		return False
	else:
		global total_nodes
		total_nodes = int(''.join(s.decode('utf-8')),16)
		return True

def read_serial():
	s = ser.read(1)
	buffer.clear()
	while s != b'T':
		if(s == b'S'):
			buffer.clear()
		else:
			buffer.append(s)
		s = ser.read(1)
	if(s == b'T'):
		buffer.append(s)
	ser.reset_input_buffer()
	ser.reset_output_buffer()



def process_data():
	nodes_list.clear()
	while len(buffer) != 0  and buffer[0] != b'T':
		if buffer[0] == b'N':
			buffer.pop(0)
			assigned_ts = int(''.join(buffer.pop(0).decode('utf-8')),16)+1

			energy_str = [x.decode('utf-8') for x in buffer[0:8]]
			energy_int = int(''.join(energy_str),16)
			del buffer[0:8]
			bitmap = []
			for byte in range(-(total_nodes // -8)): # essa locura no range é só um ceil	
				value = int(''.join(buffer.pop(0).decode('utf-8')),16)
				for bit in range(7):
					if (bool((0x01 << bit) & value)): 
						bitmap.append(byte + bit + 1)
			nodes_list.append(Node(assigned_ts,energy_int,bitmap))
	buffer.clear()

def build_matrix():
	global adjacent_matrix 
	adjacent_matrix = np.zeros((total_nodes, total_nodes),dtype=int)
	row_index = 1
	for row_index in range(len(adjacent_matrix)):
		node = None
		for it_node in nodes_list:
			if it_node.assigned_ts == row_index + 1:
				node = it_node
				break
		if len(node.bitmap) > 0:
			for neig in node.bitmap:
				adjacent_matrix[row_index][neig-1] = int(neig) if int(neig)>0 else int(0)
	if ENABLE_PRINT:
		print(adjacent_matrix)
		pass
	
def build_lpsolve_file():
	min_str = 'min:'
	connected_coord_nodes = []
	notconnected_coord_nodes = []
	bin_var = []
	for node in nodes_list:
		if node.energy != 0:
			min_str+='%6f'%(ENERGY_CONST/(node.energy/10.0))+'*x'+str(node.assigned_ts)+'+'
			neighbors = 'ConectCoordX'+str(node.assigned_ts)+':'
			for neig in node.bitmap:
				neighbors+='x'+str(neig)+'+'
			neighbors = neighbors[:-1] + '>=1;'
			connected_coord_nodes.append(neighbors)
			bin_var.append('bin x'+str(node.assigned_ts)+';')
		else:
			neighbors ='NotConetCoordX'+str(node.assigned_ts)+':'
			empty = len(neighbors)
			i = 1
			for neig in adjacent_matrix[:,(node.assigned_ts-1)]:
				neighbors += ('x'+ str(i) +'+') if neig > 0 else ''
				i+=1
			if(len(neighbors) > empty):
				neighbors = neighbors[:-1] + '>=1;'
				notconnected_coord_nodes.append(neighbors)

	min_str = min_str[:-1] + ';'
	if ENABLE_PRINT:
		print(min_str)
		print(connected_coord_nodes)
		print(notconnected_coord_nodes)
		print(bin_var)
		
if __name__ == "__main__":
	ser = serial.Serial(COM_PORT, BAUD_RATE)

	if ser.is_open == False:
		if ENABLE_PRINT:
			print('Failed to open PORT')
		exit
	
	ser.reset_input_buffer()
	ser.reset_output_buffer()
	state = 'STATE_WAIT_COMMAND'

	while(1):

		if state == 'STATE_WAIT_COMMAND':
			if wait_command():
				start_time = time.time()
				read_serial()
				process_data()
				if ENABLE_PRINT:
					print(nodes_list)	
					pass
				build_matrix()
				build_lpsolve_file()
				print("--- %s seconds ---" % (time.time() - start_time))

				state = 'STATE_WAIT_COMMAND'
				# state = 'STATE_RX_STORE'
			else:
				print(ser.read_all())
				state = 'STATE_WAIT_COMMAND'

		elif state == 'STATE_SOLVE_COOP':
			pass
		elif state == 'STATE_IDLE':
			pass
		else: #STATE_IDLE
			pass
