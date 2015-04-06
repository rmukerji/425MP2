#this file represents a chord system
from node_class import node
from math import pow, log
import thread
from threading import current_thread
from collections import namedtuple
global finish
global node_count
m = 8
size = int(pow(2, m))
chord = [] #array to represent circular chord system. Each index can either be of type node, or an integer to represent a key
channels = [] #array to communicate between one another


def print_node(index, n):
	print "_________" + " Identifier: " + str(index) + " _________"
	print "Previous: " + str(n.pred.id) + " Successor: " + str(n.succ.id)
	i = 0
	while i < len(n.finger_table):
		print "Start: " + str(n.finger_table[i][0]) + "\tSucc: " + str(n.finger_table[i][1].id)
		i+=1

def print_system():
	for i in range(0, size):
		if not isinstance(chord[i], int):
			print_node(i, chord[i])
			print "--------------------------------------"

def validate_system():
	global node_count
	for i in range(0, size):
		if not isinstance(chord[i], int):
			n = chord[i]
			k = 0
			while k < m:
				start = n.finger_table[k][0]
				l = start
				while 1:
					if not isinstance(chord[l], int):
						if chord[l].id != n.finger_table[k][1].id:
							return n.id
						else:
							break	
					l = (l + 1) % size
				k += 1
	return True				



def log2(x):
     return log(x)/log(2)

def initialize_system():
	global node_count
	node_count += 1
	n = node()
	n.pred = n
	n.succ = n
	n.id = 0
	for i in range(0, size):
		chord.append(i)
		n.key_value[i] = 0
	for i in range(0, m):
		fte = [int(pow(2, i)), n]
		n.finger_table.append(fte)
	chord[0] = n #index 0 in the chord is a node	

def create_node(num):
	n = node()
	n.id = num
	chord[num] = n
	for i in range(0, m):
		fte = [int(((num + pow(2, i)) % size)), n]
		n.finger_table.append(fte)
	return n	

def read_inputs():
	global finish
	global node_count
	while 1:
		command = raw_input('--> ')
		if "join" in command: #join command 
			node_count += 1
			num = int(command.split(" ")[1])
			if num < 0 or num > 255:
				print "ENTER VALUE BETWEEN 0 AND 255"
				continue
			if not isinstance(chord[num], int):
				print "NODE WITH IDENTIFIER " + str(num) + " ALREADY EXISTS"
				continue
			n = create_node(num)
			thread.start_new_thread(join, (n, chord[0]))
			while finish == 0:
				waiting = 1
			finish = 0	
			print_system()
			val = validate_system()
			if(val == True):
				print "CHORD IS VALID"
			else:
				print "CHORD IS INVALID AT NODE " + str(val)		
		command = ""


def find_succesor(n, ident):
	node_pred = find_predecessor(n, ident)
	return node_pred.succ

def find_predecessor(n, ident):
	temp_node = n
	global node_count
	if (node_count == 2 and ident > n.succ.id and n.id == 0):
		return  n.succ
	elif node_count == 2 and n.id == 0:
		return n
	if (node_count == 2 and ident < n.id and n.id != 0):
		return  chord[0]
	elif node_count == 2 and n.id != 0:
		return n			
	while(ident <= temp_node.id or ident > temp_node.succ.id):
		s = temp_node	
		temp_node = closest_preceding_finger(temp_node, ident)
		if temp_node == s:
			if(ident < temp_node.id):
				temp_node = temp_node.pred
			else:
				return temp_node	
	return temp_node

def closest_preceding_finger(n, ident):
	itr = m - 1
	while itr >= 0:
		if(n.id < n.finger_table[itr][1].id and n.finger_table[itr][1].id < ident):
			return n.finger_table[itr][1]
		itr -= 1			
	return n		


def join(n, n_prime):
	global finish
	global node_count
	if(node_count == 2):
		chord[0].succ = n
		n.succ = n_prime
		init_finger_table(n, n_prime)
		update_others(n)
	else:
		init_finger_table(n, n_prime)
		update_others(n)	
	finish = 1

def init_finger_table(n, n_prime):
	global node_count	
	if(n.id == size - 1): #when we add node 255 to the system
		n.succ = chord[0]
		n.finger_table[0][1] = chord[0]
	else:		
		n.finger_table[0][1] = find_succesor(n_prime, n.finger_table[0][0])
		n.succ = n.finger_table[0][1]
	n.pred = n.succ.pred
	n.pred.succ = n
	n.succ.pred = n
	i = 0
	while i < m - 1:
		if (n.finger_table[i + 1][0] == 0):
			n.finger_table[i + 1][1] = chord[0]
		elif(n.finger_table[i + 1][0] >= n.id and n.finger_table[i][1].id == 0):
			n.finger_table[i + 1][1] = n.finger_table[i][1]
		elif(n.finger_table[i + 1][0] >= n.id and n.finger_table[i + 1][0] <= n.finger_table[i][1].id):
			n.finger_table[i + 1][1] = n.finger_table[i][1]
		else:
			n.finger_table[i + 1][1] = find_succesor(n_prime, n.finger_table[i + 1][0])
		i += 1			

def update_others(n):
	global node_count
	i = 0
	if(node_count == 2):
		p = find_predecessor(n, n.id - pow(2, i) % size)
		i = 0
		while i < m and p.finger_table[i][0] <= n.id:
			p.finger_table[i][1] = n
			i+=1
		return		

	while i < m:
		f = (n.id - pow(2, i)) % size
		p = find_predecessor(n, f)
		if(p.id == n.id and f < p.id):
			p = n.pred
		if(p.id == n.id and f >= p.id):
			i += 1
			continue	
		update_finger_table(p, n, i, False)
		i += 1

def update_finger_table(n, s, i, flag):
	if(n.finger_table[i][0] == 0):
		n.finger_table[i][1] = chord[0]
	elif(s.id >= n.finger_table[i][0] and n.finger_table[i][1].id == 0):
		n.finger_table[i][1] = s
		p = n.pred
		if(flag == False):
			update_finger_table(p, s, i, True)
	elif(s.id >= n.finger_table[i][0] and s.id <= n.finger_table[i][1].id):
		n.finger_table[i][1] = s
		p = n.pred
		update_finger_table(p, s, i, False)
	

def main():
	global finish
	global node_count
	node_count = 0
	finish = 0
	initialize_system() #initializes the system with a node at position 0
	print_system()
	thread.start_new_thread(read_inputs, ())
	while 1:
		waiting = 1

main()