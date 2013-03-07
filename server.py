"""
CMPUT 297/115 - Assignment 3

Version 1.0

By: Mark H Langen

This assignment is a solo effort, and
any extra resources are cited in the code below.
"""


"""
Main route-finding program server.

Usage:
python3 server.py [graphdatafile]

The program reads requests from the stdin and writes responses to 
the stdout.
In order to use it with a networked device, pipe the input/output
as you see fit.
"""


import sys
from readgraph import read_graph
from digraph import least_cost_path
from serial import Serial

"""
Initialization:
Read in the graphdata from the specified file
"""
sourcefilename = 'edmonton-roads-digraph.txt'
argv = sys.argv[1:]
if len(argv) == 0:
	#for no args, nothing to do, use default file
	pass
elif len(argv) == 1:
	#for one arg, that arg is the file
	sourcefilename = argv[0].strip(' ')
else:
	#otherwise, there was a bad usage, bail out
	print("Invalid usage.\nExpected: server.py [graphdatafile]")
	exit(-1)

(graph, metadata) = (None, None)
#try:
(graph, metadata) = read_graph(open(sourcefilename))
#except:
#	print("Could not open source graph file `%s` for reading" % sourcefilename)
#	exit(-1)



def dist_between(node_a_id, node_b_id):
	"""
	Calculate the distance between two vertex IDs
	"""
	#get the nodes
	node_a = metadata[node_a_id]
	node_b = metadata[node_b_id]

	#calculate the distance and eturn it
	return ((node_a[0]-node_b[0])**2 + (node_b[1]-node_b[1])**2)**0.5



def dist_to(node_id, lat, lon):
	"""
	Calculate the distance from a vertex ID to a position
	"""
	node = metadata[node_id]
	return ((node[0]-lat)**2 + (node[1]-lon)**2)**0.5



def nearest_vertex(lat, lon):
	"""
	Find the nearest vertex ID in |graph| to a given position
	"""
	return min(graph.vertices(), key=lambda x: dist_to(x, lat, lon))



def cost_distance(e):
	"""
	Cost function for our path.
	Calculates the cost of an edge as the straight-line distance in 
	100000's of a degree between the two vertices that it connects.

	Test with our sample data set
	>>> a = nearest_vertex(5365488/100000, -11333914/100000)
	>>> b = nearest_vertex(5364727/100000, -11335890/100000)
	>>> int(cost_distance((a,b)))
	760

	"""
	# unpack arg
	(node_id_a, node_id_b) = e

	# get the nodes
	node_a = metadata[node_id_a]
	node_b = metadata[node_id_b]

	# get the dist between
	dist = dist_between(node_id_a, node_id_b)

	# nothing more to do. In the future we could apply more modifications
	# to the cost than just the distance here.
	# add on the turn cost factor
	turn_cost = metadata[(node_id_a, node_id_b)]
	if turn_cost:
		dist += turn_cost

	# cost is exactly the distance for now, return it, in 100000's of a degree
	return dist*100000


"""
Main loop:
Read in requests from the standard input. Each request is exactly
one line of data.
"""
if __name__ == "__main__":
	io = Serial(port = '/dev/ttyACM0', baudrate=9600)
	io.flush()
	while True:
		request = io.readline()
		request = request.decode("ASCII")

		# parse the line into the start and end positions
		[startlat, startlon, endlat, endlon] = [None,None,None,None]
		try:
			[startlat, startlon, endlat, endlon] = [int(x)/100000 for x in request.strip(' \n').split(' ')]
		except:
			#bad stuff in stream, flush it and try again
			io.flush()
			continue

		# turn those positions into the nearest verticies in the graph
		start = nearest_vertex(startlat, startlon)
		end = nearest_vertex(endlat, endlon)

		# find the least cost path
		path = least_cost_path(graph, start, end, cost_distance)

		# print some diagnostics
		print("Results for request: `%s`" % request.strip(' \n'))

		# print out the path as the result
		if path:
			# print length
			print(len(path), file=sys.stdout)
			io.write(bytes(str(len(path)) + "\n", 'ASCII'))
			for nodeid in path:
				# print each node
				node = metadata[nodeid]
				print("{} {}".format(int(node[0]*100000), int(node[1]*100000)), file=sys.stdout)
				io.write(bytes("{} {}\n".format(int(node[0]*100000), int(node[1]*100000)), 'ASCII'))
		else:
			# no valid path. The documentation does not specify what the result should be in
			# this case, so we just send back a 0 to indicate no path results were found.
			print("0")
			io.write(bytes('0\n', 'ASCII'))

		# done, on to wait for the next request (looping over sys.stdin will pause for user input, and
		# terminate the loop once EOF is reached)




	

