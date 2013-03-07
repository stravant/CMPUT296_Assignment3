"""
Graph module for directed graphs.
"""

import random

try:
    import display
except:
    print("Warning: failed to load display module.  Graph drawing will not work.")
    
class Digraph:
    """
    Directed graph.  The vertices must be immutable.

    To create an empty graph:
    >>> G = Digraph()
    >>> (G.num_vertices(), G.num_edges())
    (0, 0)

    To create a circular graph with 3 vertices:
    >>> G = Digraph([(1, 2), (2, 3), (3, 1)])
    >>> (G.num_vertices(), G.num_edges())
    (3, 3)
    """

    def __init__(self, edges = None):
        self._tosets = {}
        self._fromsets = {}

        if edges:
            for e in edges: self.add_edge(e)

    def __repr__(self):
        return "Digraph({}, {})".format(self.vertices(), self.edges())

    def add_vertex(self, v):
        """
        Adds a vertex to the graph.  It starts with no edges.
        
        >>> G = Digraph()
        >>> G.add_vertex(1)
        >>> G.vertices() == {1}
        True
        """
        if v not in self._tosets:
            self._tosets[v] = set()
            self._fromsets[v] = set()

    def add_edge(self, e):
        """
        Adds an edge to graph.  If vertices in the edge do not exist, it adds them.
        
        >>> G = Digraph()
        >>> G.add_vertex(1)
        >>> G.add_vertex(2)
        >>> G.add_edge((1, 2))
        >>> G.add_edge((2, 1))
        >>> G.add_edge((3, 4))
        >>> G.add_edge((1, 2))
        >>> G.num_edges()
        3
        >>> G.num_vertices()
        4
        """
        # Adds the vertices (in case they don't already exist)
        for v in e:
            self.add_vertex(v)

        # Add the edge
        self._tosets[e[0]].add(e[1])
        self._fromsets[e[1]].add(e[0])

    def edges(self):
        """
        Returns the set of edges in the graph as ordered tuples.

        Running time is O(m + n) where n is the number of vertices
          and m is the number of edges
        """
        return {(v, w) for v in self._tosets for w in self._tosets[v] }

    def vertices(self):
        """
        Returns the set of vertices in the graph.
        """
        return set(self._tosets.keys())

    def draw(self, filename, attr = {}):
        """
        Draws the graph into a dot file.
        """
        display.write_dot_desc((self.vertices(), self.eges()), filename, attr)

    def num_edges(self):
        m = 0
        for v in self._tosets:
            m += len(self._tosets[v])
        return m

    def num_vertices(self):
        """
        Returns the number of vertices in the graph.
        """
        return len(self._tosets)

    def adj_to(self, v):
        """
        Returns the set of vertices that contain an edge from v.

        >>> G = Digraph()
        >>> for v in [1, 2, 3]: G.add_vertex(v)
        >>> G.add_edge((1, 3))
        >>> G.add_edge((1, 2))
        >>> G.adj_to(3) == set()
        True
        >>> G.adj_to(1) == { 2, 3 }
        True
        """
        return self._tosets[v]

    def adj_from(self, v):
        """
        Returns the set of vertices that contain an edge to v.

        >>> G = Digraph()
        >>> G.add_edge((1, 3))
        >>> G.add_edge((2, 3))
        >>> G.adj_from(1) == set()
        True
        >>> G.adj_from(3) == { 1, 2 }
        True
        """
        return self._fromsets[v]

    def is_path(self, path):
        """
        Returns True if the list of vertices in the argument path are a
        valid path in the graph.  Returns False otherwise.

        >>> G = Digraph([(1, 2), (2, 3), (2, 4), (1, 5), (2, 5), (4, 5), (5, 2)])
        >>> G.is_path([1, 5, 2, 4, 5])
        True
        >>> G.is_path([1, 5, 4, 2])
        False
        >>> G.is_path([])
        True
        """
        # no input path? Is a path
        if len(path) == 0:
            return True

        elif len(path) == 1:
            #just check if the node is in the graph
            return path[0] in self._tosets

        else:
            #main case, loop over nodes
            for i in range(1,len(path)):
                if path[i] not in self._tosets[path[i-1]]:
                    return False
            return True



def random_graph(n, m):
    """
    Make a random Digraph with n vertices and m edges.

    >>> G = random_graph(10, 5)
    >>> G.num_edges()
    5
    >>> G.num_vertices()
    10
    >>> G = random_graph(1, 1)
    Traceback (most recent call last):
    ...
    ValueError: For 1 vertices, you wanted 1 edges, but can only have a maximum of 0
    """
    G = Digraph()
    for v in range(n):
        G.add_vertex(v)

    max_num_edges = n * (n-1)
    if m > max_num_edges:
        raise ValueError("For {} vertices, you wanted {} edges, but can only have a maximum of {}".format(n, m, max_num_edges))

    while G.num_edges() < m:
        G.add_edge(random.sample(range(n), 2))

    return G

def spanning_tree(G, start):  
    """ 
    Runs depth-first-search on G from vertex start to create a spanning tree.
    """
    visited = set()
    todo = [ (start, None) ]

    T = Digraph()
    
    while todo:
        (cur, e) = todo.pop()

        if cur in visited: continue

        visited.add(cur)
        if e: T.add_edge(e)

        for n in G.adj_to(cur):
            if n not in visited:
                todo.append((n, (cur, n)))
                
    return T


def least_cost_path(G, start, dest, cost):
    """
    path = least_cost_path(G, start, dest, cost)

    least_cost_path returns a least cost path in the digraph G from vertex
    start to vertex dest, where costs are defined by the cost function.
    cost should be a function that takes a single edge argument and returns
    a real-valued cost.

    if there is no path, then returns None

    the path from start to start is [start]

    >>> G = Digraph([ (1,2), (2,3), (3,4), (4,3), (4,5), (1,6), (6,7), (7,5) ])
    >>> Cost = {(1,2): 0, (2,3): 2, (3,4): 0, (4,3): 1, (4,5): 10, (1,6): 1, (6,7): 6, (7,5): 0}
    >>> least_cost_path(G, 1, 5, lambda x: Cost[x])
    [1, 6, 7, 5]

    >>> G = Digraph([ (1,2) ])
    >>> G.add_vertex(3)
    >>> least_cost_path(G, 1, 1, lambda x: 1)
    [1]
    >>> least_cost_path(G, 1, 3, lambda x: 1)
    """

    # todo[v] is the current best estimate of cost to get from start to v 
    todo = {start: 0}

    # v in visited when the vertex v's least cost from start has been determined
    visited = set()

    # parent[v] is the vertex that just precedes v in the path from start to v
    parent = {}

    while todo and (dest not in visited):
        # priority queue operation
        # remove smallest estimated cost vertex from todo list
        # this is not the efficient heap form, but it works
        # because it mins on the cost (2nd) field of the tuple of
        # items from the todo dictionary
        (cur,c) = min(todo.items(), key=lambda x: x[1])
        todo.pop(cur)

        # it is now visited, and will never have a smaller cost
        visited.add(cur)

        for n in G.adj_to(cur):
            if n in visited: 
                continue
            if n not in todo or ( c + cost((cur,n)) < todo[n] ):
                todo[n] = c + cost((cur,n))
                parent[n] = cur

    # now, if there is a path, extract it.  The graph may be disconnected
    # so in that case return None
    if dest in visited:
        path = []
        curnode = dest
        while curnode:
            path.append(curnode)
            if curnode in parent:
                curnode = parent[curnode]
            else:
                curnode = None

        # path is constructed, but in reverse order, return the reversed version
        return path[::-1]

    else:
        # no path found
        return None



def compress(walk):
    """
    Remove cycles from a walk to create a path. 
    >>> compress([1, 2, 3, 4])
    [1, 2, 3, 4]
    >>> compress([1, 3, 0, 1, 6, 4, 8, 6, 2])
    [1, 6, 2]
    """
    
    lasttime = {}

    for (i,v) in enumerate(walk):
        lasttime[v] = i

    rv = []
    i = 0
    while (i < len(walk)):
        rv.append(walk[i])
        i = lasttime[walk[i]]+1

    return rv
    
            

if __name__ == "__main__":
    import doctest
    doctest.testmod()
