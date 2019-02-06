#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 15 15:37:26 2019

@author: pragya
"""

import os
import networkx as nx
import pickle 
import pdb
from itertools import combinations
import process_json as pj
import matplotlib.pyplot as plt


import logging
logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')
#filename='log_relay_placement.txt', 
logging.disable(logging.CRITICAL)


def load_pickle(filename='pickle'): 
    # for reading also binary mode is important 
    rdfile = open(filename, 'rb')  
    logging.debug('Reading graph from pickle')  
    graph = pickle.load(rdfile) 
    logging.debug('Finished Reading')  
    #pj.draw_graph(graph, "out_graph")
    return graph
    
def make_subgraph(graph):
    main_nodes = []
    for node in graph.nodes(data=True):
        if node[1]['type']!='R':
            main_nodes.append(node[0])
            
    temp_sg = graph.subgraph(main_nodes)
    sub_graph = nx.Graph()
    sub_graph.add_nodes_from(temp_sg.nodes(data=True))
    
    for i in list(combinations(main_nodes, 2)):
        try:
            w = nx.shortest_path_length(graph, i[0], i[1], weight="weight")
        except nx.NetworkXNoPath:
            continue
        else :
            sub_graph.add_weighted_edges_from([i+(w,)])
    return sub_graph
    
def relay_placement(input_file_path):
    file_dir = os.path.dirname(input_file_path)
    file = os.path.basename(input_file_path)
    file_name, file_type = file.split('_')
    out_file_path = os.path.join(file_dir, file_name)
    
    if file_type == 'pickle':
        G = load_pickle(input_file_path)
        
    subg = make_subgraph(G)
    
    plt.figure(1)
    pj.draw_graph(subg, out_file_path+"_terminals")
    terminals = subg.nodes()
    #print (terminals)
    
    print (nx.is_biconnected(subg))
    if nx.is_connected(subg):
        mst = nx.minimum_spanning_tree(subg, 1)
        #print (T1.edges(data=True))
        expand_mst = nx.Graph()
        plt.figure(2)
        pj.draw_graph(mst, out_file_path+"_terminal_mst")
        #pdb.set_trace()
        
        #expanding the MST
        for e in mst.edges():
            temp = G.subgraph(nx.shortest_path(G, e[0], e[1]))
            expand_mst.add_nodes_from(temp.nodes(data=True))
            expand_mst.add_edges_from(temp.edges(data=True))
        plt.figure(3)
        pj.draw_graph(expand_mst, out_file_path+"_expanded_mst")
        
        steiner = nx.minimum_spanning_tree(expand_mst)
        while True:
            n = dict(nx.degree(steiner))
            bad_leaf = [k for k,v in n.items() if v == 1 and k not in terminals]
            print(bad_leaf)
            if not len(bad_leaf):
                break
            steiner.remove_nodes_from(bad_leaf)
        plt.figure(4)
        pj.draw_graph(steiner, out_file_path+"_RNPC")
        pj.store_pickle(steiner, out_file_path+"RNPC_pickle")
    else:
        print ("Terminals of the given graph do not lie in a single sonnected component. Thus it cannot be processed further")