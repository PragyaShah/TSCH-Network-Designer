#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  8 13:46:30 2019

@author: Pragya
"""

import json
import os
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

def store_pickle(graph, filename='pickle'): 
    # Its important to use binary mode 
    wrfile = open(filename, 'wb') 
    logging.debug('Writing graph to pickle')
    # source, destination 
    pickle.dump(graph, wrfile) 
    logging.debug('Finished Writing')                     
    wrfile.close() 
    
def make_graphml(graph, filename="gml"):
    nx.write_graphml(graph, filename)
    logging.debug('Finished making graphml')

def make_dotfile(Graph, filename='dot'):
    graph = Graph.copy()
    for n in graph:                                                                                           
        graph.node[n]['pos'] = '"%f,%f!"'%(graph.node[n]['posx'], graph.node[n]['posy'])
    logging.debug('Writing graph to dotfile')
    nx.drawing.nx_pydot.write_dot(graph, filename)
    print ('\n\nNow run the command "neato -Tps '+filename+' >'+filename+'.ps" from the directory containing '+filename+'.dot\n\n')
    
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
        n_type = nx.get_node_attributes(graph, 'type')
        for i in list(combinations(pos, 2)):
            d = distance.euclidean(pos[i[0]], pos[i[1]])
            logging.debug(str(i)+' '+str(d))
            if d<=limit:
                weight = 0
                if n_type[i[0]]=='R': weight+=1
                if n_type[i[1]]=='R': weight+=1
                valid_edges.append(i+(weight,))
    return (valid_edges)

def draw_graph(graph, filename="graph.png"):
    nx.draw(graph, pos= get_pos(graph), with_labels = True)  
    bbox = {'ec':[1,1,1,0], 'fc':[0,1,1,0]}  # hack to label edges over line (rather than breaking up line)
    edge_labels = nx.get_edge_attributes(graph, 'weight')
    nx.draw_networkx_edge_labels(graph, pos=get_pos(graph), edge_labels=edge_labels, bbox=bbox)

    #plt.axis('on')
    #plt.grid('on')
    plt.savefig(filename)
    #plt.show()
    
def process_json(input_file_path, limit, param = 'distance'):
    file_dir = os.path.dirname(input_file_path)
    file = os.path.basename(input_file_path)
    file_name, file_ext = os.path.splitext(file)
    out_file_path = os.path.join(file_dir, file_name)
    
    with open(input_file_path) as f:
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
    store_pickle(G, out_file_path+'_pickle')
    make_graphml(G, out_file_path+'_gml')
    make_dotfile(G, out_file_path+'_dot')
    
    draw_graph(G, out_file_path+'_graph')
    
    return (G)