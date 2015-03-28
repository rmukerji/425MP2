import socket
import thread
import sys
#-------------------------------------------------------------------------------
# So the way I am thinking about it is that there is going to be a thread for the coordinator which is a server who is going to be reading messages from the 
# command line and there is a thread for each node which is going to be a client. Initially, a node is going to launched and will wait to receive messages from
# the coordinator in handle_request. For example, if there is a "join p" request the coordinator got, then he broadcasts to all the nodes that are currently on 
# the system and tells them what the request is. The individual nodes change their local FPT and once they're done, they send a message back to the coordinator.
# The coordinator waits until he receives acks from all the nodes. 
#-------------------------------------------------------------------------------

TCP_IP = "127.0.0.1"
TCP_PORT = 4000
num_keys = 256
num_nodes = 0
coordinator_sockets = []
chord = []


def initialize_system():
	for i in range(0, num_keys):
		chord.append(i)


def handle_request(server):
	while 1:
		data = server.recv(100)
		data = data.replace("\n", "")


def join_node():
	global TCP_PORT
	global num_nodes
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.connect((TCP_IP, TCP_PORT))
	num_nodes +=1
	TCP_PORT+=1
	if num_nodes == 1:
		initialize_system()
	handle_requests(server)

def coordinator():	
	global coordinator_sockets

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.bind((TCP_IP, TCP_PORT))
	s.listen(1)

	coordinator_sockets.append(s)
	thread.start_new_thread(join_node, ())

	while 1:
		data = raw_input("")
		if len(data) > 0:
			if data == "join p":
				s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
				s.bind((TCP_IP, TCP_PORT))
				s.listen(1)
				coordinator_sockets.append(s)
				thread.start_new_thread(join_node, ())


def main():
	thread.start_new_thread(coordinator, ())
	thread.start_new_thread(join_node, ())

main()