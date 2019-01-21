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
import pickle
import pdb

import logging
logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')
#filename='log_process_json.txt', 
logging.disable(logging.CRITICAL)

#json_file = 'in.json'#to be removed
#param = 'distance'#to be removed
#limit = 35 #to be removed

def store_pickle(graph, filename='graph_pickle'): 
    # Its important to use binary mode 
    wrfile = open(filename, 'ab') 
    logging.debug('Writing graph to pickle')
    # source, destination 
    pickle.dump(graph, wrfile) 
    logging.debug('Finished Writing')                     
    wrfile.close() 
    
def make_graphml(graph, filename="test.graphml"):
    nx.write_graphml(graph, filename)
    logging.debug('Finished making graphml')

def make_dotfile(Graph, filename='graph.dot'):
    graph = Graph.copy()
    for n in graph:                                                                                           
        graph.node[n]['pos'] = '"%f,%f!"'%(graph.node[n]['posx'], graph.node[n]['posy'])
    logging.debug('Writing graph to dotfile')
    nx.drawing.nx_pydot.write_dot(graph, filename)
    print ('\n\nNow run the command "neato -Tps graph.dot >graph.ps" from the directory containing graph.dot\n\n')
    
def get_pos(graph):
    px = nx.get_node_attributes(graph, 'posx')
    py = nx.get_node_attributes(graph, 'posy')
    #print p
    pos = {}
    for n in px: 
        pos[n]=(px[n],py[n])
    #pos = tuple(map(int, p.split(',')))
    return(pos)

def edge_calc(graph, limit, param = 'distance'):
    valid_edges = []
    if param == 'distance':
        pos = get_pos(graph)
        for i in list(combinations(pos, 2)):
            d = distance.euclidean(pos[i[0]], pos[i[1]])
            logging.debug(str(i)+' '+str(d))
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
        #G.nodes[node['id']]['pos'] = '"%f,%f!"'%(G.nodes[node['id']]['posx'], G.nodes[node['id']]['posy'])
        
    logging.debug(str(list(G.nodes(data=True))))
        
    G.add_weighted_edges_from(edge_calc(G, limit, param))
    
    #making different kinds of o/p files
    store_pickle(G)
    make_graphml(G)
    make_dotfile(G)
    
    nx.draw(G, pos= get_pos(G), with_labels = True)  
    plt.axis('on')
    plt.grid('on')
    plt.savefig("path_graph.png")
    plt.show()
    return (G)