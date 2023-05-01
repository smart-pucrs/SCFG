import numpy as np
import networkx as nx

from seqsvs_vs import check_SVS

def split(CS, v, G, S, maxsize=np.infty):
    CS_singletons = set()

    for C in CS:
        if len(C) == 1:
            CS_singletons.add(C)
            continue

        c_prime = {frozenset([ag]) for ag in C}

        if len(c_prime) > maxsize or len(c_prime.intersection(S)) > 1:
            CS_singletons = CS_singletons.union(break_up_constraints(C, v, G, S, maxsize))
        else:            
            G_prime = G.subgraph([frozenset([a]) for a in C])

            for comp in nx.connected_components(G_prime):             
                comp = frozenset().union(*comp)   
                CS_singletons = CS_singletons.union(break_up_contribution(comp, v))

    return frozenset(CS_singletons)

def merge(CS, CS_prime, v, R, G, S, maxsize=np.infty, add_function=None, level=0, found=False):
    if len(CS_prime) <= 1:
        return None
    
    best_e = None
    l_CS = list(CS_prime)
    np.random.shuffle(l_CS)

    to_break = False
    for i, C in enumerate(l_CS, start=1):
        if to_break: break

        for C_prime in l_CS[i:]:
            if len(C)+len(C_prime) > max(maxsize):
                continue

            if len(C.intersection(S))+len(C_prime.intersection(S)) > 1:
                continue

            G_prime = G.subgraph([frozenset([a]) for a in C.union(C_prime)])
            if not nx.is_connected(G_prime):
                continue
            
            new_CS = C.union(C_prime)
            best_e = (C, C_prime, new_CS)  
            to_break = True
            break

    if best_e == None:
        return None
    
    CS_prime = (CS_prime.union({best_e[2]})).difference({best_e[0]}).difference({best_e[1]})    
    if R(CS, CS_prime):
        add_function(CS, CS_prime, level=level)
        if check_SVS(CS_prime, G, S, maxsize):
            return CS_prime
        
    return merge(CS, CS_prime, v, R, G, S, maxsize, add_function, level)

def break_up_constraints(C, v, G, S, Z):
    CS = set()

    C = {frozenset([ag]) for ag in C}

    for s in C.intersection(S):
        CS.add(s)

    for ag in C.difference(S):
        best_e = None

        for C_prime in CS:
            if len(C_prime)+1 > Z:
                continue

            is_connected = False
            for _, ag_prime in G.edges(ag):
                if len(ag_prime.intersection(C_prime)) > 0:
                    is_connected = True
                    break

            if is_connected:
                if np.random.random(1) < 0.5:
                    best_e = C_prime      

        if best_e == None:
            CS.add(ag)
        else:
            CS.add(best_e.union(ag))
            CS = CS.difference({best_e})
    return CS    

def break_up_contribution(C, v):
    CS, C_prime = set(), C
    
    for ag in C:
        if np.random.random(1) < 0.5:
            C_prime = C_prime.difference({ag})
            CS.add(frozenset([ag]))

    if len(C_prime) > 0:
        CS.add(C_prime)

    return CS
    