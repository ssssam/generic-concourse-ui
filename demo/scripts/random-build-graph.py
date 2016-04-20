#!/usr/bin/env python3
# Copyright 2016 Codethink Ltd.
# Apache 2.0 license

'''Generate a random build graph in 'node-link' JSON format.'''


import networkx
import networkx.readwrite.json_graph

import json
import sys


INPUT_NAMES = '/usr/share/dict/words'

N_NODES = 1000
N_EDGES = 2000


# Return a random graph with a fixed number of nodes and edges.
g = networkx.gnm_random_graph(N_NODES, N_EDGES, directed=True)

# Assign names
with open(INPUT_NAMES) as f:
    lines = f.readlines()

    for i in g.nodes():
        line_mult = len(lines) / g.number_of_nodes()
        name = lines[int(i * line_mult)].strip()
        g.node[i]['name'] = name

json.dump(networkx.readwrite.json_graph.node_link_data(g), sys.stdout)
