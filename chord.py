#this file represents a chord system
from node_class import node
from math import pow, log
import time
import thread
from threading import Lock
from collections import namedtuple
import sys
from random import randint
global finish
global message_count
global find_count

m = 8
size = int(pow(2, m))
chord = [] #array to represent circular chord system. Each index can either be of type node, or an integer to represent a key
rem_node_channel = []
rem_update_channel = []
update_others_channel = []
update_finger_table_channel = []
find_pred_channel = []
find_succ_channel = []
rem_update_lock = Lock()
update_lock = Lock()


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

def log2(x):
     return log(x)/log(2)

def initialize_system():
	n = node()
	n.pred = n
	n.succ = n
	n.id = 0
	for i in range(0, size):
		chord.append(i)
		rem_node_channel.append([])
		rem_update_channel.append([])
		update_others_channel.append([])
		update_finger_table_channel.append([])
	for i in range(0, m):
		fte = [int(pow(2, i)), n]
		n.finger_table.append(fte)
	chord[0] = n #index 0 in the chord is a node
	thread.start_new_thread(wait_for_command, (n.id,))	

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
	global message_count
	global find_count
	import random
	while 1:
		global finish
		command = raw_input('--> ')
		if "join" in command: #join command 
			message_count = 0	
			num = int(command.split(" ")[1])
			if num < 0 or num >= size:
				print "ENTER VALUE BETWEEN 0 AND " + str(size)
				continue
			if not isinstance(chord[num], int):
				print "NODE WITH IDENTIFIER " + str(num) + " ALREADY EXISTS"
				continue
			n = create_node(num)
			thread.start_new_thread(join, (n, chord[0]))
			done = False
			while(done != True or finish == 0):
				done = check_done()	
			#print_system()
			finish = 0
		elif "find" in command: #find command
			find_count = 0
			parsed_command = command.split(" ")
			node_used_to_find = int(parsed_command[1])
			key = int(parsed_command[2])
			if node_used_to_find < 0 or node_used_to_find >= size or key < 0 or key >= size:
				print "Please enter values between 0 and " + str(size) + " for p and k"
				continue
			if isinstance(chord[node_used_to_find], int):
				print str(node_used_to_find) + " is an integer. Please enter a valid node id."
				continue
			print "Key " + str(key) +  " is located at node " + str(find_node(chord[node_used_to_find], key))
			while finish == 0:
				waiting = 1
			finish = 0
		elif "leave" in command:
			message_count = 0	
			node = int(command.split(" ")[1])
			if node < 0 or node > size:
				print "Please enter a value between 0 and " + str(size)
				continue
			if isinstance(chord[node], int):
				print str(node) + " is an integer. Please enter a valid node id."
				continue
			rem_node_channel[node].insert(0, chord[node]) #signal the node to leave by writing in shared queue
			done = False
			while(done != True or finish == 0):
				done = check_done()
			finish = 0
		elif "show all" in command:
			show_all(chord[0])
			while finish == 0:
				waiting = 1
			finish = 0	
		elif "show" in command:
			node = int(command.split(" ")[1])
			if node < 0 or node > size:
				print "Please enter a value between 0 and " + str(size)
				continue
			if isinstance(chord[node], int):
				print str(node) + " is an integer. Please enter a valid node id."
				continue	
			show(chord[node])	
		else:
			print "Please enter a valid command"
		command = ""

def wait_for_command(ident):
	global finish
	global message_count
	while 1:
		#for remove_node
		if(len(rem_node_channel[ident]) > 0):	
			#remove_node(rem_node_channel[node.id][0])
			thread.start_new_thread(remove_node, (rem_node_channel[ident][0], ))
			rem_node_channel[ident].pop()
		if(len(rem_update_channel[ident]) > 0):
		#for remove_update
			size = len(rem_update_channel[ident])
			n = rem_update_channel[ident][size - 1][0]
			s = rem_update_channel[ident][size - 1][1]
			i = rem_update_channel[ident][size - 1][2]
			remove_update(n, s, i)
			rem_update_channel[ident].pop()
		if(len(update_others_channel[ident]) > 0):
			thread.start_new_thread(update_others, (update_others_channel[ident][0], ))
			update_others_channel[ident].pop()
		if(len(update_finger_table_channel[ident]) > 0):
			#print "Identity: " + str(ident)
			size = len(rem_update_channel[ident])
			n = update_finger_table_channel[ident][size - 1][0]
			s = update_finger_table_channel[ident][size - 1][1]
			i = update_finger_table_channel[ident][size - 1][2]
			update_finger_table(n, s, i)
			update_finger_table_channel[ident].pop()		
		
		if(isinstance(chord[ident], int)): #the node has left
			return		

def check_remove_done():
	for i in range(0, size):
		if(len(rem_update_channel[i]) > 0):
			return False
	return True		

def check_join_done():
	for i in range(0, size):
		if(len(update_finger_table_channel[i]) > 0):
			return False
	return True	

def show(node):
	global f
	counter = 1
	#print "______________ ID: " + str(node.id) + " ______________"
	f.write(str(node.id) + " ")	
	if(node.id == 0 and node.pred.id == 0): #0 is the only node in the system
		for i in range(0, size):
			#sys.stdout.write(str(i) + "\t")
			#if counter % 5 == 0:  
				#sys.stdout.write("\n")	
			f.write(str(i) + " ")		
			counter += 1		
		return		
	if(node.id == 0):
		p = node.pred.id + 1
		#sys.stdout.write(str(0) + "\t")
		f.write(str(0) + " ")
		counter += 1		
		while p < size:
			#sys.stdout.write(str(p) + "\t")
			#if counter % 5 == 0:
				#sys.stdout.write("\n")	
			f.write(str(p) + " ")	
			counter += 1
			p += 1
		#print "\n"	
	else:	
		p = (node.pred.id + 1) % size
		while p != (node.id + 1) % size:
			#sys.stdout.write(str(p) + "\t")
			#if counter % 5 == 0:
				#sys.stdout.write("\n")	
			f.write(str(p) + " ")	
			counter += 1
			p = (p + 1) % size
		#print "\n"
	f.write("\n")	

def show_all(s):
	global finish
	global f
	global message_count
	show(s)
	tracker = s.succ
	while tracker.id != s.id:
		show(tracker)
		tracker = tracker.succ	
		#sys.stdout.write("\n")
	finish = 1

def check_done():
	global message_count
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

def find_node(n_prime, key):
	global message_count
	global finish
	find_succesor(n_prime, key)
	while len(find_succ_channel) == 0:
		waiting = 1
	node = find_succ_channel[0]
	find_succ_channel.pop()	
	finish = 1
	return node.id

def find_succesor(n, ident):
	global message_count
	if not isinstance(chord[int(ident)], int):
		find_succ_channel.append(chord[int(ident)])
	else:
		find_predecessor(n, ident)
		while len(find_pred_channel) == 0:
			waiting = 1
		node_pred = find_pred_channel[0]
		find_pred_channel.pop()	
		find_succ_channel.append(node_pred.succ)
def find_predecessor(n, ident):
	global message_count
	global find_count
	temp_node = n
	if not isinstance(chord[int(ident)], int):
		find_pred_channel.append(chord[int(ident)])
	else:	
		while(ident < temp_node.id or ident >= temp_node.succ.id):
			s = temp_node	
			temp_node = closest_preceding_finger(temp_node, ident)
			#print "Find Predecessor"
			message_count += 1
			find_count += 1
			if temp_node == s:
				if(ident < temp_node.id):
					temp_node = temp_node.pred
				else:
					find_pred_channel.append(temp_node)
					break;
		if(len(find_pred_channel) == 0):				
			find_pred_channel.append(temp_node)

def closest_preceding_finger(n, ident):
	global message_count
	itr = m - 1
	while itr >= 0:
		if(n.id < n.finger_table[itr][1].id and n.finger_table[itr][1].id < ident):
			return n.finger_table[itr][1]
		itr -= 1			
	return n		

def remove_node(n):
	global finish
	global message_count
	p = n.pred
	s = n.succ
	p.succ = s
	s.pred = p
	i = 0
	while i < m:
		f = (n.id - pow(2, i)) % size
		find_predecessor(n, f)
		while len(find_pred_channel) == 0:
			waiting = 1
		p = find_pred_channel[0]
		find_pred_channel.pop()	
		rem_update_lock.acquire()
		rem_update_channel[p.id].insert(0, [p, n, i])
		message_count += 1
		rem_update_lock.release()
		i += 1
	chord[n.id] = n.id
	finish = 1

def remove_update(n, s, i):
	global message_count
	if n.finger_table[i][1].id == s.id:
		n.finger_table[i][1] = s.succ
		p = n.pred
		rem_update_lock.acquire()
		rem_update_channel[p.id].insert(0, [p, s, i])
		message_count += 1
		rem_update_lock.release()	

def join(n, n_prime):
	init_finger_table(n, n_prime)
	update_others_channel[n.id].insert(0, n)
	wait_for_command(n.id)

def init_finger_table(n, n_prime):
	global message_count
	find_succesor(n_prime, n.finger_table[0][0])
	while len(find_succ_channel) == 0:
		waiting = 1
	n.finger_table[0][1] = find_succ_channel[0]
	find_succ_channel.pop()	
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
			find_succesor(n_prime, n.finger_table[i + 1][0])
			while len(find_succ_channel) == 0:
				waiting = 1
			n.finger_table[i + 1][1] = find_succ_channel[0]
			find_succ_channel.pop()	
		i += 1			

def update_others(n):
	global message_count
	global finish
	i = 0	
	while i < m:
		f = (n.id - pow(2, i)) % size
		find_predecessor(n, f)
		while len(find_pred_channel) == 0:
			waiting = 1
		p = find_pred_channel[0]
		find_pred_channel.pop()	
		if(p.id == n.id and f < p.id):
			p = n.pred
		if(p.id == n.id and f >= p.id):
			i += 1
			continue
		update_lock.acquire()	
		update_finger_table_channel[n.id].insert(0, [p, n, i])
		#print "Update Others"
		message_count += 1
		update_lock.release()
		i += 1
	finish = 1		

def update_finger_table(n, s, i):
	global message_count
	if(n.finger_table[i][0] == 0):
		n.finger_table[i][1] = chord[0]	
	elif(s.id >= n.finger_table[i][0] and n.finger_table[i][1].id == 0):
		n.finger_table[i][1] = s
		p = n.pred
		update_lock.acquire()	
		update_finger_table_channel[p.id].insert(0, [p, s, i])
		#print "update_finger_table"
		#message_count += 1
		update_lock.release()
	elif(s.id >= n.finger_table[i][0] and s.id < n.finger_table[i][1].id):
		n.finger_table[i][1] = s
		p = n.pred
		update_lock.acquire()	
		update_finger_table_channel[p.id].insert(0, [p, s, i])
		#print "update_finger_table"
		message_count += 1
		update_lock.release()		

def main():
	global finish
	global filename
	global f
	global message_count
	global find_count
	find_count = 0
	message_count = 0
	filename = sys.argv[2]
	f = open(filename,'wb')
	finish = 0
	initialize_system() #initializes the system with a node at position 0
	#print_system()
	thread.start_new_thread(read_inputs, ())
	while 1:
		waiting = 1

main()