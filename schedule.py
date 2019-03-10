#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 30 16:08:46 2019

@author: pragya
"""


import os
import networkx as nx
import process_json as pj

def initiate(RNPC):
    for node in RNPC.nodes(data=True):
        if node[1]['type']=='S':
            RNPC.nodes[node[0]]['Bmsg']=True
    
            
def scheduling(input_file_path):
    file_dir = os.path.dirname(input_file_path)
    file = os.path.basename(input_file_path)
    file_name, file_type = file.split('_')
    out_file_path = os.path.join(file_dir, file_name)
    
    if file_type == 'pickle':
        RNPC = pj.load_pickle(input_file_path)
        
    #print (str(list(RNPC.nodes(data=True))))
    #print (str(list(RNPC.edges(data=True))))
    
    for node in RNPC.nodes(data=True):
        RNPC.add_node(node[0], Rfree = True, Bmsg = False)
        if node[1]['type']=='S':
            RNPC.nodes[node[0]]['Bmsg']=True
            
    root = None
    n=0
    pj.draw_graph(RNPC, out_file_path+'_graph')
    for node, n_type in RNPC.nodes(data='type'):
        if n_type == 'BS':
            root = node
            #print (n_type)
        elif n_type == 'S':
            n=n+1
        
    bfs_nodes = dict(nx.bfs_successors(RNPC,root))
    dfs_nodes = list(nx.dfs_edges(RNPC, root))
    tstree_qcount={}
    for u, v in dfs_nodes:
        if u==root:
            tsroot = v
            tstree_qcount[tsroot]=0
            if RNPC.nodes[v]['type']=='S':
                tstree_qcount[tsroot]+=1
        else:
            if RNPC.nodes[v]['type']=='S':
                tstree_qcount[tsroot]+=2
    #bfs_nodes =[root]+[v for u, v in nx.bfs_edges(RNPC, root)]
    qi = max(tstree_qcount[tsroot] for tsroot in tstree_qcount )
    l_bound = max(n, qi)
    #l_bound = n
    
    f = open(out_file_path+ '_schedule.txt','w')
    
    
    for i in range(5):
        initiate(RNPC)
        f.write("initialized")
        for l in range(l_bound):
            f.write('\n--------------------'+str(l)+'\n')
            for v in bfs_nodes:
                if (RNPC.nodes[v]['Rfree'] and (not RNPC.nodes[v]['Bmsg'])) or RNPC.nodes[v]['type']=='BS':
                    full_child = []
                    for c in bfs_nodes[v]:
                        if RNPC.nodes[c]['Bmsg']:
                            full_child += [c]
                    if len(full_child) == 0:
                        continue
                    elif len(full_child) ==1:
                        RNPC.nodes[v]['Bmsg']=True
                        RNPC.nodes[v]['Rfree']=False
                        RNPC.nodes[full_child[0]]['Bmsg']=False
                        RNPC.nodes[full_child[0]]['Rfree']=False
                        f.write(str(full_child[0])+'->'+str(v)+' ')
                    else:
                        max_msg = 0
                        child = full_child[0]
                        
                        for fc in full_child:
                            msg_count = 0
                            if fc in bfs_nodes:
                                for cc in bfs_nodes[fc]:
                                    if RNPC.nodes[cc]['Bmsg']: 
                                        msg_count += 1
                                    if cc in bfs_nodes:
                                        for ccc in bfs_nodes[fc]:
                                            if RNPC.nodes[ccc]['Bmsg']: 
                                                msg_count += 1
                            
                            if msg_count> max_msg:
                                child = fc
                        
                        RNPC.nodes[v]['Bmsg']=True
                        RNPC.nodes[v]['Rfree']=False
                        RNPC.nodes[child]['Bmsg']=False
                        RNPC.nodes[child]['Rfree']=False
                        f.write(str(child)+'->'+str(v)+' ')
                        
            for node in RNPC.nodes(data=True):
                RNPC.nodes[node[0]]['Rfree']=True
                
    f.close()

    
    print(bfs_nodes)
    print(dfs_nodes)
    print (tstree_qcount)
    print (qi)
    print (l_bound)
    print (root)
    #print (str(list(RNPC.nodes(data='type'))))
    #print (str(list(RNPC.edges(data=True))))
    
    
    
    
    
    
    
    
    
    
    