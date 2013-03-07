
from digraph import Digraph
import math

def read_graph(input_file):
	"""
	Read in Digraph data from a file, and return it as a tuple containing a Digraph 
	as well as a map of metadata with vertex positions and edge names.
	Returns:
		(digraph, { (node id or edge tuple): (position or edge name) })
	"""

	# # graph and metadata to populate
	# graph = Digraph()
	# metadata = {}

	# # set of vertices that we have read in. Used to check that
	# # we aren't adding verts through |add_edge| that won't have any
	# # location metadata.
	# vert_set = set()

	# # process each line in the file
	# for line in input_file:

	#     # strip all trailing whitespace
	#     line = line.rstrip()

	#     fields = line.split(",")
	#     type = fields[0]

	#     if type == 'V':
	#         # got a vertex record
	#         (id,lat,long) = fields[1:]

	#         # vertex id's should be ints
	#         id=int(id)

	#         # lat and long are floats
	#         lat=float(lat)
	#         long=float(long)

	#         vert_set.add(id)
	#         graph.add_vertex(id)
	#         metadata[id] = (lat,long)
	        
	#     elif type == 'E':
	#         # got an edge record
	#         (start,stop,name) = fields[1:]

	#         # vertices are ints
	#         start=int(start)
	#         stop=int(stop)
	#         e = (start,stop)

	#         if start not in vert_set:
	#         	raise Exception("Vertex %d is an endpoint for an edge but has no metadata" % start)
	#         if stop not in vert_set:
	#         	raise Exception("Vertex %d is an endpoint for an edge but has no metadata" % stop)

	#         # get rid of leading and trailing quote " chars around name
	#         name = name.strip('"')

	#         graph.add_edge(e)
	#         metadata[e] = name
	#     else:
	#         # weird input
	#         raise Exception("Error: weird line |{}|".format(line))

	vert_map = {}  # vert_id => {at = (lat,lon), ine = set(), oute = set()}
	edge_map = {}  # (id,id) => name

	for line in input_file:

	    # strip all trailing whitespace
	    line = line.rstrip()

	    fields = line.split(",")
	    type = fields[0]

	    if type == 'V':
	        # got a vertex record
	        (id,lat,long) = fields[1:]

	        # vertex id's should be ints
	        id=int(id)

	        # lat and long are floats
	        lat=float(lat)
	        long=float(long)

	        #todo
	        vert_map[id] = {'at': (lat,long), 'id': id, 'ine': set(), 'oute': set()}
	        
	    elif type == 'E':
	        # got an edge record
	        (start,stop,name) = fields[1:]

	        # vertices are ints
	        start=int(start)
	        stop=int(stop)
	        e = (start,stop)

	        # get rid of leading and trailing quote " chars around name
	        name = name.strip('"')

	        #todo
	        edge_map[(start,stop)] = name

	    else:
	        # weird input
	        raise Exception("Error: weird line |{}|".format(line))

	
	graph = Digraph()

	cached_aux_verts = {}
	def get_aux_verts(e):
		if e not in cached_aux_verts:
			aux_vert = {}

	# first assign ine and oute on verts 
	for e in edge_map:
		vert_map[e[0]]['oute'].add(e)
		vert_map[e[1]]['ine'].add(e)

	# metadata
	metadata = {}

	# now, make the aux vert set
	aux_vert_map = {}  # {vert_id => {adjacent_id => aux_vert_id}}
	aux_vert_current_id = 1
	for v_id in vert_map:
		my_aux_verts = {}
		vdat = vert_map[v_id]
		for e in vdat['ine']:
			my_aux_verts[e[0]] = aux_vert_current_id
			aux_vert_current_id += 1
		for e in vdat['oute']:
			my_aux_verts[e[1]] = aux_vert_current_id
			aux_vert_current_id += 1
		for id in my_aux_verts.values():
			metadata[id] = vdat['at']
			graph.add_vertex(id)
		aux_vert_map[v_id] = my_aux_verts

	# aux verts have been created, add the main edges
	for (a,b) in edge_map:
		graph.add_edge((aux_vert_map[a][b], aux_vert_map[b][a]))
		metadata[(aux_vert_map[a][b], aux_vert_map[b][a])] = 0

	# and finally, we need to add the junction virtual edges
	for v_id in vert_map:
		vdat = vert_map[v_id]
		# for each incomming edge, join it to each outgoing edge
		for (a,b) in vdat['ine']:
			in_aux_vert_id = aux_vert_map[v_id][a]
			for (b,c) in vdat['oute']:
				out_aux_vert_id = aux_vert_map[v_id][c]
				#calculate cost
				cost = 0
				if len(vdat['ine']) == 1 and len(vdat['oute']) == 1:
					#ignore turn cost for nodes that just represent curves
					cost = 0
				else:
					#use the angle
					at_a = vert_map[a]['at']
					at_b = vert_map[b]['at']
					at_c = vert_map[c]['at']
					dir_1 = (at_b[0]-at_a[0],at_b[1]-at_a[1])
					dir_2 = (at_c[0]-at_b[0],at_c[1]-at_b[1])
					theta = math.acos( (dir_1[0]*dir_2[0]+dir_1[1]*dir_2[1]) / \
						( (dir_1[0]**2+dir_1[1]**2)**0.5 * (dir_2[0]**2+dir_2[1]**2)**0.5 ) * 0.9999)
					cost = theta*10

				#add
				graph.add_edge((in_aux_vert_id, out_aux_vert_id))
				metadata[(in_aux_vert_id, out_aux_vert_id)] = cost

	#return the data
	return (graph, metadata)
