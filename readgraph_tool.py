"""
    python3 readgraph.py [ digraph-file ]

Takes a csv (comma separated values) text file containing the vertices
and edges of a street digraph and converts it into a digraph instance.

If the optional argument digraph-file is supplied, reads that, otherwise
takes input from stdin
"""
import sys
from readgraph import read_graph

# throw away executable name before processing command line arguments
argv = sys.argv[1:]

# if filename is supplied, use that, otherwise use stdin
if argv:
    digraph_file_name = argv.pop(0)
    digraph_file = open(digraph_file_name, 'r')
else:
    digraph_file = sys.stdin

(graph, md) = read_graph(digraph_file)

if True:
    print("Done\n:", md)
