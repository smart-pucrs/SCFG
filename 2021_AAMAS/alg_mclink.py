import os, sys; sys.path.append(os.path.dirname(os.path.realpath(__file__)))
import logging
import itertools
import math
import time
import numpy as np
import pandas as pd
from collections import defaultdict
from gen_input import gen_A, gen_H

def V_R_S(CS, CS_prime):
    if len(CS) == 0:
        return True 
    if len(CS) == len(CS_prime):
        return False 
    for c in CS_prime:
        b = [c <= temp for temp in CS]
        if not any(b):
            return False
    return True

def feasible_sequence(FCSS, R):
    for i in range(1, len(FCSS)):
        if not R(FCSS[i-1], FCSS[i]):
            return False
    return True
def feasible(i, CS, FCSS, R):
    if len(FCSS) == 1: return True
    if i==0:
        return R(CS, FCSS[i+1])
    elif i==len(FCSS)-1:
        return R(FCSS[i-1], CS)
    else:
        return R(FCSS[i-1], CS) and R(CS, FCSS[i+1])

def slf(v, c1,c2):
    # return v[c1.union(c2)] - v[c1] - v[c2]
    return v(c1.union(c2)) - v(c1) - v(c2)
def fill_in_table(index, FCSS, v, R):
    PL = empty_table(FCSS[index])
    l = list(PL.columns)
    for i in range(len(l)):
        for j in range(i+1, len(l)):          
            CS_hat = build_cs(l, l[i], l[j],  as_set=True)
            if feasible(index, CS_hat, FCSS, R):
                PL.iloc[i][j] = slf(v, l[i], l[j])
    return PL
def empty_table(l):
    return pd.DataFrame(np.full((len(l), len(l)), -np.inf), index=l, columns=l)
def build_cs(old_l_cs, c1, c2, as_set=False):
    if as_set:
        return {c for c in old_l_cs+[c1.union(c2)] if c!=c1 and c!=c2}
    else:
        return [c for c in old_l_cs+[c1.union(c2)] if c!=c1 and c!=c2]

def mclink(A, H, R):
    FCSS = [[frozenset([a]) for a in A]]*len(H)
    M_hat = [math.inf]*(len(H))
        
    if not feasible_sequence(FCSS, R): 
        i = 0
        while i < len(H)-1:   
            PL = fill_in_table(i, FCSS, H[i], R)   
            M_hat[i] = PL.values.max()
            if M_hat[i] > -math.inf:                
                j, k = np.unravel_index(PL.values.argmax(), PL.values.shape)
                FCSS[i] = build_cs(list(PL.columns), PL.columns[j], PL.columns[k])        
                i +=1
            else:
                if i == 0:
                    return  {'v':0, 'h': [(0,{})]*len(H)} 
                else: 
                    i -= 1
    i = 0
    while max(M_hat) > 0:
        PL = fill_in_table(i, FCSS, H[i], R) 
        M_hat[i] = PL.values.max()
        if M_hat[i] > 0:
            j, k = np.unravel_index(PL.values.argmax(), PL.values.shape)
            FCSS[i] = build_cs(list(PL.columns), PL.columns[j], PL.columns[k])        
        i +=1
        if i >= len(H):
            i = 0      

    # temp = [(sum([H[i][c] for c in cs]), cs) for i, cs in enumerate(FCSS)]
    temp = [(sum([H[i](c) for c in cs]), cs) for i, cs in enumerate(FCSS)]
    return {'v': sum([cs[0] for cs in temp]), 'h': temp} 
    
# def cf(c):
#     return np.random.normal(len(c), len(c))
def cf(c):
    return math.pow(len(c), 2)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logging.info("Multiple C-Link")
    
    n = 4
    h = 3
    R = V_R_S
    A = gen_A(n)
    H = gen_H(A, h, cf, table=False)  

    logging.info(f" Instance: n={len(A)}, h={len(H)}")
    start_time = time.time()
    FCSS_star = mclink(A, H, R)
    logging.info(f' elapsed time (s): {time.time()-start_time}')
    logging.info(f' Total Value = {FCSS_star["v"]}')
    for value, CS in FCSS_star['h']:
        logging.info(f' V({CS}) = {value}')    