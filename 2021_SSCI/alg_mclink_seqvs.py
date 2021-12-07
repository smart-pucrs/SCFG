import os, sys; sys.path.append(os.path.dirname(os.path.realpath(__file__)))
import logging
import math
import numpy as np
import pandas as pd
from seqvs_vs import check_VS, v_pivotal

def feasible(R, G, S, CS, CS_prime):
    return R(CS, CS_prime) and check_VS(CS_prime, G, S)
def feasible_CSS(R, Pi, CSS):
    for i in range(len(CSS)):
        CS_prime = {} if i==0 else CSS[i-1] 
        if not R(CS_prime, CSS[i]) and check_VS(CSS[i], Pi[i][1], Pi[i][0]):
            return False
    return True

def func_matrix(v, VS, c1,c2):
    return v_pivotal(v, VS, c1.union(c2)) - v_pivotal(v, VS, c1) - v_pivotal(v, VS, c2)

def fill_in_table(t, index, FCS, H, R, VS):
    l = list(t.columns)
    for i in range(len(l)):
        for j in range(i+1, len(l)):
            CS = {} if index==0 else FCS[index-1]            
            if feasible(R, VS[0], VS[1], CS, build_cs(l, l[i], l[j],  as_set=True)):
                t.iloc[i][j] = func_matrix(H[index], VS, l[i], l[j])
            else:
                t.iloc[i][j] = -np.inf
    return t
def empty_table(l):
    return pd.DataFrame(np.full((len(l), len(l)), -np.inf), index=l, columns=l)
def build_cs(old_l_cs, c1, c2, as_set=False):
    if as_set:
        return {c for c in old_l_cs+[c1.union(c2)] if c!=c1 and c!=c2}
    else:
        return [c for c in old_l_cs+[c1.union(c2)] if c!=c1 and c!=c2]

def mclink(A, H, Pi, R):
    CS = {frozenset([a]) for a in A}
    CSS = [CS]*len(H)
    M_hat = [math.inf]*len(H)
        
    i = 0
    while not feasible_CSS(R, Pi, CSS): 
        PL = fill_in_table(empty_table(CSS[i]), i, CSS, H, R, Pi[i])    
        M_hat[i] = PL.values.max()
        if M_hat[i] > -math.inf:
            j, k = np.unravel_index(PL.values.argmax(), PL.values.shape)
            CSS[i] = build_cs(list(PL.columns), PL.columns[j], PL.columns[k], as_set=True)        
        i += 1            
        if i >= len(CSS):
            if max(M_hat) == -np.inf:
                return  {'v':0, 'h': [(0,{})]*len(H)} 
            i = 0
    FCSS_star = [CS for CS in CSS] 
    i = 0
    while max(M_hat) > 0:
        PL = fill_in_table(empty_table(CSS[i]), i, CSS, H, R, Pi[i])    
        M_hat[i] = PL.values.max()
        if M_hat[i] > 0:
            j, k = np.unravel_index(PL.values.argmax(), PL.values.shape)
            CSS[i] = build_cs(list(PL.columns), PL.columns[j], PL.columns[k], as_set=True)    
            i +=1   
        else:
            if i>0 and not feasible(R, Pi[i][0], Pi[i][1], CSS[i-1], CSS[i]):
                if M_hat[i-1] <= 0:
                    break
                else:
                    i -=1
            else:
                i +=1
        if i >= len(H):
            i = 0 
            FCSS_star = [CS for CS in CSS]

    temp = [(sum([v_pivotal(H[i], Pi[i], c) for c in cs]), cs) for i, cs in enumerate(FCSS_star)]
    return {'v': sum([cs[0] for cs in temp]), 'h': temp} 

if __name__ == "__main__":
    import time
    from gen_seqvs_input import load_instance
    from gen_R import V_R_1, V_R_2, V_R_3, V_R_4
    PATH_TO_FILE = os.path.dirname(os.path.realpath(__file__))+"/results/ssci_instances"
    logging.basicConfig(level=logging.DEBUG)
    logging.info("Multiple C-Link variant for SEQVS")

    A, H, Pi = load_instance(PATH_TO_FILE, "instance30_A=5_H=4_cf=ndcs.json")

    logging.info(f" Instance: n={len(A)}, h={len(H)}")
    start_time = time.time()
    FCSS = mclink(A, H, Pi, V_R_2)
    logging.info(f' elapsed time (s): {time.time()-start_time}')
    logging.info(f'Total Value = {FCSS["v"]}')
    for v, CS in FCSS['h']:
        logging.info(f'V({CS}) = {v}')    