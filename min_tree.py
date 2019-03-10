#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  5 14:40:01 2019

@author: pragya
"""

import os
import math
import networkx as nx
import pdb
from itertools import combinations
import process_json as pj
import matplotlib.pyplot as plt

import logging
logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')
#filename='log_relay_placement.txt', 
logging.disable(logging.CRITICAL)



    
def remove_relay(graph):
    reduced = graph.copy()
    for e in reduced.edges(data=True):
        reduced.edges[e[0], e[1]]['link'] = []
    for node in graph.nodes(data=True):
        if node[1]['type']=='R':
#            plt.figure(node[0])
#            pj.draw_graph(reduced, "try/x_"+str(node[0]))
            r_neighbour = [neighbour for relay, neighbour in reduced.edges(node[0])]
            for i in list(combinations(r_neighbour , 2)):
                w1 = math.inf 
                if reduced.has_edge(i[0], i[1]):
                    w1 = reduced.edges[i[0], i[1]]['weight']
                w2 = reduced.edges[node[0], i[1]]['weight']+reduced.edges[i[0], node[0]]['weight']
                if (w1>w2):
                    reduced.add_edge(i[0], i[1], weight=w2, link=reduced.edges[node[0], i[1]]['link']+[node[0]]+reduced.edges[i[0], node[0]]['link'])
            reduced.remove_node(node[0])
            #x = input("proceed?")
            
#    for e in reduced.edges(data=True):
#        print(reduced.edges[e[0], e[1]]['link'])
    return reduced

def min_tree(input_file_path):
    file_dir = os.path.dirname(input_file_path)
    file = os.path.basename(input_file_path)
    file_name, file_type = file.split('_')
    out_file_path = os.path.join(file_dir, file_name)
    test_path = os.path.join(file_dir, 'trial', 'try_')
    
    if file_type == 'pickle':
        G = pj.load_pickle(input_file_path)
        
    reduced_graph = remove_relay(G)
    
#    plt.figure(1)
#    pj.draw_graph(reduced_graph, out_file_path+"_terminals")
    fig = 1
    plt.figure(fig)
    pj.draw_graph(reduced_graph, test_path+"terminal"+str(fig))
    fig+=1
    #terminals = reduced_graph.nodes()
    #print (terminals)
    
    #finding the sink (Base Station)
    for node in reduced_graph.nodes(data=True):
        if node[1]['type']=='BS':
            sink_id = node[1]['id']
            break
        
    
    print (nx.is_biconnected(reduced_graph))
    if nx.is_connected(reduced_graph):
        
        #CMST begins================================================
    
        #initialize:----------------------------------
        Tree = nx.Graph()
        
        #getting hop counts and max hop counts
        hop_tuples = []
        for node in reduced_graph.nodes():
            reduced_graph.nodes[node]['hops'] = nx.shortest_path_length(reduced_graph, sink_id, node)
            if reduced_graph.nodes[node]['hops']>1:
                hop_tuples+=[(node, reduced_graph.nodes[node]['hops'])]
        hop_tuples = sorted(hop_tuples, key = lambda x : x[1])
        max_hop_count = hop_tuples[-1][1]
        
        single_hop = []
        #finding and connecting roots of top sub-trees        
        for sink,branch_root in reduced_graph.edges(sink_id):
            single_hop += [branch_root]
            temprary = G.subgraph([sink]+reduced_graph.edges[sink, branch_root]['link']+[branch_root])
            Tree.add_nodes_from(temprary.nodes(data=True))
            Tree.add_edges_from(temprary.edges(data=True))
#        plt.figure(2)
#        pj.draw_graph(Tree, out_file_path+"_tree")
        plt.figure(fig)
        pj.draw_graph(Tree, test_path+"tree"+str(fig))
        fig+=1
        #updating reduced tree - removing unrequired edges
        # is this needed?
        for i in list(combinations(single_hop , 2)):
            if reduced_graph.has_edge(i[0], i[1]):
                reduced_graph.remove_edge(i[0], i[1])      
#        plt.figure(1)
#        pj.draw_graph(reduced_graph, out_file_path+"_terminals")
        plt.figure(fig)
        pj.draw_graph(reduced_graph, test_path+"terminal"+str(fig))
        fig+=1
        #UPDATES
        #defining branches, their loads and their components
        branches = {}
        dfs_edges = list(nx.dfs_edges(Tree, source=sink_id))
        for parent, child in dfs_edges:
            if parent==sink_id:
                branch = child
                branches[branch]={}
                branches[branch]['nodes']=set([child])
                branches[branch]['load']=0
                if Tree.nodes[child]['type']=='S':
                    branches[branch]['load']+=1
            else:
                branches[branch]['nodes']=set([child])|branches[branch]['nodes']
                if Tree.nodes[child]['type']=='S':
                    branches[branch]['load']+=1
        #print (dfs_edges)
        #print (branches)
        
        
        #UPDATES
        #making growth sets, parent sets and hop sets
        all_sets = {}
        hop_set = {}
        #print(hop_tuples)
        for node, hop in hop_tuples:
            if hop in hop_set:
                hop_set[hop]=set([node])|hop_set[hop]
            else:
                hop_set[hop]=set([node])
                
            all_sets[node] = {'growth':set([]), 'parents':set([])}
            for vertex,adj_vert in reduced_graph.edges(node):
                #if parent
                if reduced_graph.nodes[adj_vert]['hops']<reduced_graph.nodes[vertex]['hops']:
                    all_sets[node]['parents']=set([adj_vert])|all_sets[node]['parents']
                
                elif reduced_graph.nodes[adj_vert]['hops']>reduced_graph.nodes[vertex]['hops']:
                    all_sets[node]['growth']=set([adj_vert])|all_sets[node]['growth']
                    
        #print(all_sets)
        #print(hop_set)
        
        #iteration
        
        for h in range(2, max_hop_count+1):
            done=[]
            left_tuple=[]
            #directly connecting nodes with single parent
            for node in hop_set[h]:
                if len(all_sets[node]['parents'])==1:
                    done+=[node]
                    temp = G.subgraph([node]+reduced_graph.edges[node, all_sets[node]['parents'][0]]['link']+all_sets[node]['parents'])
                    Tree.add_nodes_from(temp.nodes(data=True))
                    Tree.add_edges_from(temp.edges(data=True))
                else:
                    left_tuple += [(node, len(all_sets[node]['growth']))]
            
#            plt.figure(2)
#            pj.draw_graph(Tree, out_file_path+"_tree")
            plt.figure(fig)
            pj.draw_graph(Tree, test_path+"tree"+str(fig))
            fig+=1
            #updating reduced tree - removing unrequired edges
            # is this needed?
            for i in done:
                for j in hop_set[h]:
                    if reduced_graph.has_edge(i, j):
                        reduced_graph.remove_edge(i, j)      
#            plt.figure(1)
#            pj.draw_graph(reduced_graph, out_file_path+"_terminals")
            plt.figure(fig)
            pj.draw_graph(reduced_graph, test_path+"terminal"+str(fig))
            fig+=1
            #updating branches, their loads and their components
            dfs_edges = list(nx.dfs_edges(Tree, source=sink_id))
            for parent, child in dfs_edges:
                if parent==sink_id:
                    branch = child
                    branches[branch]={}
                    branches[branch]['nodes']=set([child])
                    branches[branch]['load']=0
                    if Tree.nodes[child]['type']=='S':
                        branches[branch]['load']+=1
                else:
                    branches[branch]['nodes']=set([child])|branches[branch]['nodes']
                    if Tree.nodes[child]['type']=='S':
                        branches[branch]['load']+=1
                        
            
            while len(left_tuple)>0:
                left_tuple = sorted(left_tuple, key = lambda x : x[0])
                left_tuple = sorted(left_tuple, key = lambda x : x[1])
                node = left_tuple[0][0]
                left_tuple_temp = left_tuple[1:]
                left_tuple=[]
                metric_tuple = []
                for branch in branches:
                    if len(branches[branch]['nodes'] & all_sets[node]['parents'])>0:
                         #generate the search set if h<max_hop_count
                         for parent in (branches[branch]['nodes'] & all_sets[node]['parents']):
                             ss= set([])
                             relay_set=set([])
                             temp_redgraph = reduced_graph.copy()
                             for i in done:
                                 if temp_redgraph.has_edge(node, i):
                                     temp_redgraph.remove_edge(node, i) 
                             for p in all_sets[node]['parents']:
                                 if temp_redgraph.has_edge(node, p):
                                     temp_redgraph.remove_edge(node, p) 
                             for c in all_sets[node]['growth']:
                                 flag = 0
                                 for cp in all_sets[c]['parents']:
                                     if cp!=node and flag==0:
                                         for path in nx.all_simple_paths(temp_redgraph, source=cp, target=sink_id, cutoff=h):
                                             if len(set(path) & branches[branch]['nodes'])==0: 
                                                 flag =1
                                                 break
                                 if flag==0:
                                     ss = ss|set([c])
                                     relay_set=relay_set|set(reduced_graph.edges[node, c]['link'])
                             #print ('ss = '+str(ss))
                             #TODO - replace with link weight
                             relay_set = relay_set|set(reduced_graph.edges[node, parent]['link'])
                             relay_count = len(relay_set-branches[branch]['nodes'])
                             metric = branches[branch]['load']+1+len(ss)
                             # checking if branches are fusing
                             relay_flag=0
                             for b in branches:
                                 if b!=branch:
                                     if len(relay_set & branches[b]['nodes'])>0:
                                         relay_flag=1
                                         break
                             if (relay_flag ==0):
                                 metric_tuple += [(metric, relay_count, branch, parent, ss)]
                #TODO - devise how to choose the best parent within a branch 
                metric_tuple = sorted(metric_tuple, key = lambda y : y[1])
                metric_tuple = sorted(metric_tuple, key = lambda y : y[0])
                #TODO - add search set addition and remove them from further hop metrix and their links too
                temp = G.subgraph([node]+reduced_graph.edges[node, metric_tuple[0][3]]['link']+[metric_tuple[0][3]])
                Tree.add_nodes_from(temp.nodes(data=True))
                Tree.add_edges_from(temp.edges(data=True))
                for n in metric_tuple[0][4]:
                    temp = G.subgraph([n]+reduced_graph.edges[n, node]['link']+[node])
                    Tree.add_nodes_from(temp.nodes(data=True))
                    Tree.add_edges_from(temp.edges(data=True))
#                plt.figure(2)
#                pj.draw_graph(Tree, out_file_path+"_tree")
                plt.figure(fig)
                pj.draw_graph(Tree, test_path+"tree"+str(fig))
                fig+=1
                #updating reduced tree - removing unrequired edges
                # is this needed?
                for i in hop_set[h]:
                    if reduced_graph.has_edge(node, i):
                        reduced_graph.remove_edge(node, i) 
                for p in all_sets[node]['parents']:
                    if p!=metric_tuple[0][3]:
                        reduced_graph.remove_edge(node, p) 
                for n in metric_tuple[0][4]:
                    hop_set[h+1] = hop_set[h+1]-set([n])
                    for i in hop_set[h+1]:
                        if reduced_graph.has_edge(n, i):
                            reduced_graph.remove_edge(n, i)
                    for p in all_sets[n]['parents']:
                        if p!=node:
                            reduced_graph.remove_edge(n, p)
#                plt.figure(1)
#                pj.draw_graph(reduced_graph, out_file_path+"_terminals")
                plt.figure(fig)
                pj.draw_graph(reduced_graph, test_path+"terminal"+str(fig))
                fig+=1
                
                done+=[node]
                
                #updating branches, their loads and their components
                dfs_edges = list(nx.dfs_edges(Tree, source=sink_id))
                for parent, child in dfs_edges:
                    if parent==sink_id:
                        branch = child
                        branches[branch]={}
                        branches[branch]['nodes']=set([child])
                        branches[branch]['load']=0
                        if Tree.nodes[child]['type']=='S':
                            branches[branch]['load']+=1
                    else:
                        branches[branch]['nodes']=set([child])|branches[branch]['nodes']
                        if Tree.nodes[child]['type']=='S':
                            branches[branch]['load']+=1
                #TODO - may need to change these for higher hop count nodes as well
                #updating growth sets and parent sets
                for n, a in left_tuple_temp:
                    all_sets[n] = {'growth':set([]), 'parents':set([])}
                    for vertex,adj_vert in reduced_graph.edges(n):
                        #if parent
                        if reduced_graph.nodes[adj_vert]['hops']<reduced_graph.nodes[vertex]['hops']:
                            all_sets[n]['parents']=set([adj_vert])|all_sets[n]['parents']
                
                        elif reduced_graph.nodes[adj_vert]['hops']>reduced_graph.nodes[vertex]['hops']:
                            all_sets[n]['growth']=set([adj_vert])|all_sets[n]['growth']
                            
                    left_tuple += [(n, len(all_sets[n]['growth']))]
            
            
        plt.figure(fig)
        pj.draw_graph(reduced_graph, out_file_path+"_skeletontree")
        plt.figure(fig+1)
        pj.draw_graph(Tree, out_file_path+"_fulltree")
        pj.store_pickle(Tree, out_file_path+"balancedtree_pickle")
    else:
        print ("Terminals of the given graph do not lie in a single sonnected component. Thus it cannot be processed further")