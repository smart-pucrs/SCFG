import os, sys; sys.path.append(os.path.dirname(os.path.realpath(__file__)))
import networkx as nx

def v_pivotal(v, VS, C):
    pi = VS[1].intersection(C)
    if len(pi) == 1:
        a = next(iter(pi))
        return VS[2][a]*v[C] + VS[3][a]
    else:
        return VS[4]*v[C] + VS[5]

def val(v, VS, CS):
    value = 0
    for C in CS:
        value += v_pivotal(v, VS, C)
    return value
    
def V(H, Pi, FCS):
    return sum([val(H[i], Pi[i], CS) for i, CS in enumerate(FCS)])

def check_VS(CS, G, S):
    for C in CS:
        if len(C) > 1: 
            if len(C.intersection(S)) > 1:
                return False
            G_prime = G.subgraph(C)
            if not nx.is_connected(G_prime):
                return False
    return True