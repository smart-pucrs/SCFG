import os, sys; sys.path.append(os.path.dirname(os.path.realpath(__file__)))
import networkx as nx

def V_seq(CSS, H):
    value = 0
    for i, CS in enumerate(CSS):
        for C in CS:
            value += cf_v(C,H[i])
    return value

def V_cs(CS, v):
    return sum([cf_v(C,v) for C in CS])

def cf_v(C, v):
    if isinstance(v, dict):
        return v[C]
    else:
        return v(C)

def check_SVS(CS, G, S, Z):
    for C in CS:
        if len(C) not in Z:
            return False
        
        if len(C) > 1: 
            if len(C.intersection(S)) > 1:
                return False
            
            G_prime = G.subgraph([frozenset([a]) for a in C])
            if not nx.is_connected(G_prime):
                return False
            
    return True

def check_SVS_no_graph(CS, S, Z):
    for C in CS:
        if len(C) not in Z:
            return False
        if len(C) > 1: 
            if len(C.intersection(S)) > 1:
                return False
    return True