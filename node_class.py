#this class defines a node including its variables and member functions

class node:
	
	def __init__(self):
		self.id = 0
		self.pred = 0
		self.succ = 0
		self.key_value = {}
		self.finger_table = []

