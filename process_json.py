#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  8 13:46:30 2019

@author: Pragya
"""

import json
import networkx as nx
import matplotlib.pyplot as plt
from scipy.spatial import distance
from itertools import combinations

#json_file = 'in.json'#to be removed
#param = 'distance'#to be removed
#limit = 35 #to be removed

def edge_calc(graph, limit, param = 'distance'):
    valid_edges = []
    if param == 'distance':
        pos = nx.get_node_attributes(graph, 'pos')
        for i in list(combinations(pos, 2)):
            d = distance.euclidean(pos[i[0]], pos[i[1]])
            #print (i,d)
            if d<=limit:
                valid_edges.append(i+(d,))
    return (valid_edges)

def process_json(json_file, limit, param = 'distance'):
    with open(json_file) as f:
        node_data = json.load(f)
        
    G = nx.Graph()
    
    for node in node_data['nodes']:
        G.add_node(node['id'])
        for key in node:
            G.nodes[node['id']][key] = node[key]
        
    G.add_weighted_edges_from(edge_calc(G, limit, param))
   
    nx.draw(G, pos= nx.get_node_attributes(G, 'pos'), with_labels = True)  
    plt.axis('on')
    plt.grid('on')
    plt.savefig("path_graph.png")
    plt.show()
    return (G)