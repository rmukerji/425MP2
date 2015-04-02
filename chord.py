#this file represents a chord system
from node_class import node
from math import pow, log
import thread
from threading import current_thread
from collections import namedtuple
finger_table_entry = namedtuple("entry", "start succ")
global finish
m = 8
size = int(pow(2, 8))
chord = [] #array to represent circular chord system. Each index can either be of type node, or an integer to represent a key
channels = [] #array to communicate between one another


def print_node(index, n):
	print "_________" + " Identifier: " + str(index) + " _________"
	print "Previous: " + str(n.pred.id) + " Successor: " + str(n.succ.id)
	i = 0
	while i < len(n.finger_table):
		print n.finger_table[i]
		i+=1

def print_system():
	for i in range(0, size):
		if not isinstance(chord[i], int):
			print_node(i, chord[i])

def log2(x):
     return log(x)/log(2)

def initialize_system():
	n = node()
	n.pred = n
	n.succ = n
	n.id = 0
	for i in range(0, size):
		chord.append(i)
		n.key_value[i] = 0
	for i in range(0, m):
		start = pow(2, i)
		fte = finger_table_entry(start = int(start), succ = int(0))
		n.finger_table.append(fte)
	chord[0] = n #index 0 in the chord is a node	

def read_inputs():
	global finish
	while 1:
		command = raw_input('--> ')
		if "join" in command:
			num = int(command.split(" ")[1])
			n = node()
			n.id = num
			chord[num] = n
			thread.start_new_thread(join, (n, chord[0]))
			while finish == 0:
				waiting = 1
		command = ""


def find_succesor(n, ident):
	node_pred = find_predecessor(n, ident)
	return node_pred.succ.id

def find_predecessor(n, ident):
	temp_node = n
	while(ident <= temp_node.id or ident > temp_node.succ.id):
		#print ident, temp_node.id, temp_node.succ
		temp_node = closest_preceding_finger(temp_node, ident)
		if(n == temp_node):
			break;
	return temp_node

def closest_preceding_finger(n, ident):
	itr = m - 1
	while itr >= 0:
		#print n.id, n.finger_table[itr][1], ident
		if(n.id < n.finger_table[itr][1] and n.finger_table[itr][1] < ident):
			return n.finger_table[itr][1]
		itr -= 1			
	return n		



def join(n, n_prime):
	global finish
	init_finger_table(n, n_prime)
	update_others(n)
	finish = 1

def init_finger_table(n, n_prime):				
	n.finger_table[1][1] = find_succesor(n_prime, n.finger_table[1][0])
	n.succ = n.finger_table[1][1]
	n.pred = n.succ.pred
	n.succ.pred = n
	i = 0
	while i < m - 2:
		if(n.finger_table[i + 1][0] >= n.id and n.finger_table[i + 1][0] < n.finger_table[i][1]):
			n.finger_table[i + 1][1] = n.finger_table[i][1]
		else:
			n.finger_table[i + 1][1] = find_succesor(n_prime, n.finger_table[i + 1][0])
		i += 1		

def update_others(n):
	i = 0
	while i < m:
		p = find_predecessor(n, (n.id - pow(2, i - 1)) % size)
		update_finger_table(p, n, i)

def update_finger_table(n, s, i):
	if(s.id >= n.id and s.id < n.finger_table[i][1]):
		n.finger_table[i][1] = s
		p = n.predecessor
		update_finger_table(p, s, i)
	

def main():
	global finish
	finish = 0
	initialize_system() #initializes the system with a node at position 0
	print_system()
	thread.start_new_thread(read_inputs, ())
	while 1:
		waiting = 1

main()