#this file represents a chord system
from node_class import node
from math import pow, log
import thread
from collections import namedtuple
finger_table_entry = namedtuple("entry", "start int succ")
m = 256
chord = [] #array to represent circular chord system. Each index can either be of type node, or an integer

def print_node(index, n):
	print "_________" + " Identifier: " + str(index) + " _________"
	print "Previous: " + str(n.previous) + " Successor: " + str(n.successor)
	i = 0
	#print n.key_value
	while i < len(n.finger_table):
		print n.finger_table[i]
		i+=1

def print_system():
	for i in range(0, m):
		if not isinstance(chord[i], int):
			print_node(i, chord[i])

def log2(x):
     return log(x)/log(2)

def initialize_system():
	n = node()
	for i in range(0, m):
		chord.append(i)
		n.key_value[i] = 0
	for i in range(0, int(log2(m))):
		start = pow(2, i) % m
		end = (start + pow(2, i)) % m
		fte = finger_table_entry(start = int(start), int = (int(start), int(end)), succ = int(0))
		n.finger_table.append(fte)
	chord[0] = n	

def read_inputs():
	while 1:
		command = raw_input('--> ')
		print command
		command = ""

def main():
	initialize_system() #initializes the system with a node at position 0
	print_system()
	thread.start_new_thread(read_inputs, ())
	while 1:
		waiting = 1

main()