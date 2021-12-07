import os, sys; sys.path.append(os.path.dirname(os.path.realpath(__file__)))
import itertools
import numpy as np
import networkx as nx
import math
import json

def _powerset(iterable):
    s = list(iterable)
    return itertools.chain.from_iterable(itertools.combinations(s, r) for r in range(len(s)+1))

def gen_A(n):
    return ['a'+str(i) for i in range(1,n+1)]    

def gen_H(A, h, cf, table=True):
    if (table):
        return [{c: cf(c) for c in map(frozenset, _powerset(A))} for i in range(h)]   
    else:
        return [cf] * h 

def gen_Pi(A, h, config, rate_pi=None):
    Pi = []
    for i in range(h):        
        S = gen_pivotal(A, max(2, math.ceil(len(A)/2))) if rate_pi == None else gen_pivotal(A, max(2, math.ceil(len(A)/rate_pi)))
        Pi.append((gen_G_randomly(A, config[i]),
                S, 
                {a: 1 for a in S},
                {a: 0 for a in S},
                1,
                0))
    return Pi
def gen_Pi_fixed(A, h):
    Pi = []
    for i in range(h):
        S = {'a1', 'a2'}
        G = gen_G_randomly(A, 1)
        alpha = {a: np.random.normal(2, 1) for a in S} 
        beta = {a: np.random.normal(10, 4) for a in S} 
        x = np.random.uniform(0.8, 2)
        y = 0
        Pi.append([G, S, alpha, beta, x, y])
    return Pi

# def gen_pivotal(A, n_pivotals):
#     return {'a'+str(i) for i in range(1, n_pivotals+1)}
def gen_pivotal(A, n_pivotals):
    n_pi = np.random.randint(0, n_pivotals+1)
    indexes = np.arange(1, len(A)+1)
    np.random.shuffle(indexes)
    return {'a'+str(indexes[i]) for i in range(n_pi)}

def gen_G_randomly(A:list, p:float) -> nx.Graph:
    iG = nx.Graph()
    for a in A:
        iG.add_node(a)
    for i, a1 in enumerate(A[:-1], start=1):
        for a2 in A[i:]:
            if np.random.uniform(0, 1) <= p:
                # iG.add_edge(a1, a2, weight=np.random.uniform(0.8, 1)) 
                iG.add_edge(a1, a2) 
    return iG

def gen_F(S, f):
    return {a: f(a) for a in S}  


def gen_single_instance(n, h, cf, rate_pi, p_edges, id=None):
    import os, sys; sys.path.append(os.path.dirname(os.path.realpath(__file__)))
    import jsonpickle
    PATH_FILE = os.path.dirname(os.path.realpath(__file__))

    A = gen_A(n)   
    H = gen_H(A, h, cf)   
    Pi = gen_Pi(A, h, [p_edges]*h, rate_pi)

    info = {}
    info['A'] = A
    info['H'] = jsonpickle.encode(H)
    info['Pi'] = jsonpickle.encode(Pi)

    from datetime import datetime
    if id==None:
        file_name = f"{PATH_FILE}/instances/instance_A={n}_H={h}_cf={cf.__name__}.json"
    else:
        file_name = f"{PATH_FILE}/instances/instance{id}_A={n}_H={h}_cf={cf.__name__}.json"
    f = open(file_name,"w")
    f.write(json.dumps(info))
    f.close()
def load_instance(path, file_name):
        import jsonpickle

        info = None
        with open(f"{path}/{file_name}", 'r+') as _file:
            info = jsonpickle.decode(_file.read())
        
        A = info['A']
        H = jsonpickle.decode(info['H'])
        for i in range(len(H)):
            H[i] = {eval(k): v for k, v in H[i].items()} 
        Pi = jsonpickle.decode(info['Pi'])

        return A, H, Pi