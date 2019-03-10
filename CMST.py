#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 24 12:57:45 2019

@author: pragya
"""
import os
import networkx as nx
import pickle 
import pdb
from itertools import combinations
import process_json as pj
import matplotlib.pyplot as plt

# =============================================================================
# This function takes the stiener tree generated by relay_placement.py and 
# adds edges between nodes who fall into each others range 
# and also are part of the RNPC stiener tree.
# This network is then fed to the CMST algorithm
# =============================================================================

def CMST(fullgraph_path, RNPC_path):
    file_dir = os.path.dirname(fullgraph_path)
    file = os.path.basename(fullgraph_path)
    file_name, file_type = file.split('_')
    out_file_path = os.path.join(file_dir, file_name)
    
    #the RNPC graph
    inp_graph = pj.load_pickle(RNPC_path)
    #original full graph
    full_graph = pj.load_pickle(fullgraph_path)
    
    
    #adding the valid edges to the graph
    for node_pair in list(combinations(inp_graph.nodes(), 2)):
        #print (i)
        if full_graph.has_edge(node_pair[0],node_pair[1]):
            temp = full_graph.subgraph([node_pair[0],node_pair[1]])
            inp_graph.add_edges_from(temp.edges(data=True))
    plt.figure(1)
    pj.draw_graph(inp_graph, out_file_path+"_full_tree")
    
    #CMST begins================================================
    
    #initialize:
    Tree = nx.Graph()
    
    #finding the sink (Base Station)
    for node in inp_graph.nodes(data=True):
        if node[1]['type']=='BS':
            sink_id = node[1]['id']
            break
        
    #getting hop counts and max hop counts
    hop_tuples = []
    for node in inp_graph.nodes():
        inp_graph.nodes[node]['hops'] = nx.shortest_path_length(inp_graph, sink_id, node)
        if inp_graph.nodes[node]['hops']>1:
            hop_tuples+=[(node, inp_graph.nodes[node]['hops'])]
    hop_tuples = sorted(hop_tuples, key = lambda x : x[1])
    max_hop_count = hop_tuples[-1][1]
    #print(hop_tuples)
    
    #finding and connecting roots of top sub-trees
    branch_roots = [branch_root for sink,branch_root in inp_graph.edges(sink_id)]
    temp = inp_graph.subgraph([sink_id]+branch_roots)
    Tree.add_nodes_from(temp.nodes(data=True))
    Tree.add_edges_from(temp.edges(data=True))
    
    #making growth sets, parent sets and hop sets
    all_sets = {}
    hop_set = {}
    for node, hop in hop_tuples:
        if hop in hop_set:
            hop_set[hop]+=[node]
        else:
            hop_set[hop]=[node]
            
        all_sets[node] = {'growth':[], 'parents':[]}
        for vertex,adj_vert in inp_graph.edges(node):
            #if parent
            if inp_graph.nodes[adj_vert]['hops']<inp_graph.nodes[vertex]['hops']:
                all_sets[node]['parents']+=[adj_vert]
            
            elif inp_graph.nodes[adj_vert]['hops']>inp_graph.nodes[vertex]['hops']:
                all_sets[node]['growth']+=[adj_vert]
                
    for h in range(2, max_hop_count+1):
        node_gs_tuple=[]
        #directly connecting nodes with single parent
        for node in hop_set[h]:
            if len(all_sets[node]['parents'])==1:
                temp = inp_graph.subgraph([node]+all_sets[node]['parents'])
                Tree.add_nodes_from(temp.nodes(data=True))
                Tree.add_edges_from(temp.edges(data=True))
            else:
                node_gs_tuple += [(node, len(all_sets[node]['growth']))]
        
        node_gs_tuple = sorted(node_gs_tuple, key = lambda x : x[0])
        node_gs_tuple = sorted(node_gs_tuple, key = lambda x : x[1])
        for node, gs_size in node_gs_tuple:
            
            
            
            
    #initializing branch loads
    for b_root in branch_roots:
        Tree.nodes[b_root]['load']=1        
    
    
    
    
    