#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 12 13:13:25 2019

@author: pragya
"""
import random
import os
import json

#def generate_random_node

def generate_random_test_graph(json_file_name, sources, relays, x_limit=50, y_limit=50):
    file_dir = json_file_name
    filepath = os.path.join(file_dir, (json_file_name+'.json'))
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    graph = {}
    graph["nodes"]=[]
    BS = {
    	"id": 1, 
    	"posx": round(random.uniform(0,x_limit),1),
    	"posy": round(random.uniform(0,y_limit),1), 	 
    	"type": "BS",
    	"tx_pow": -3, 
    	"rx_sens": -90
    }
    graph["nodes"].append(BS)
    
    for i in range(sources):
        S = {
        	"id": i+2, 
        	"posx": round(random.uniform(0,x_limit),1),
        	"posy": round(random.uniform(0,y_limit),1), 	 
        	"type": "S",
        	"tx_pow": -3, 
        	"rx_sens": -90
        }
        graph["nodes"].append(S)
        
    for i in range(relays):
        R = {
        	"id": i+2+sources, 
        	"posx": round(random.uniform(0,x_limit),1),
        	"posy": round(random.uniform(0,y_limit),1), 	 
        	"type": "R",
        	"tx_pow": -3, 
        	"rx_sens": -90
        }
        graph["nodes"].append(R)
        
    with open(filepath, 'w+') as outfile:  
        json.dump(graph, outfile, indent=4)

