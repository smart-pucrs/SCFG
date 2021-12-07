import os, sys; sys.path.append(os.path.dirname(os.path.realpath(__file__)))
import logging
import numpy as np
from collections import defaultdict
from seqvs_vs import check_VS, val

def sdp(A, H, Pi, G_R):
    f = defaultdict(lambda: -np.infty)
    t = defaultdict(list)

    for CS in G_R(A, len(H), {}):
        VS = Pi[0]
        if check_VS(CS, VS[0], VS[1]):
            f[CS] = val(H[0], VS, CS)
            t[CS] = [CS]
    for i in range(1,len(H)):
        f_prime = defaultdict(lambda: -np.infty)
        t_prime = defaultdict(list)
        for CSS in t.values():
            CS_prime = CSS[-1]
            for CS in G_R(A, len(H), CS_prime):
                if check_VS(CS, Pi[i][0], Pi[i][1]):
                    value = f[CS_prime] + val(H[i], VS, CS)
                    if value > f_prime[CS]:
                        f_prime[CS] = value
                        t_prime[CS] = CSS + [CS]   
        (f, t) = (f_prime, t_prime)

    if len(f) > 0:
        index = max(f, key=f.get)
        max_v = f[index]
        FCSS = t[index]
        return {'v': max_v, 'h': [(val(H[i], Pi[i], cs), cs) for i, cs in enumerate(FCSS)]} 
    else:
        return {'v': 0, 'h': [(0, {}) for i in range(len(H))]} 

if __name__ == "__main__":
    import time
    import tracemalloc
    from gen_R import G_R_1, G_R_2, G_R_3, G_R_4
    from gen_seqvs_input import load_instance    
    PATH_TO_FILE = os.path.dirname(os.path.realpath(__file__))+"/results/ssci_instances"
    logging.basicConfig(level=logging.DEBUG)
    logging.info("SDP Algorithm")

    A, H, Pi = load_instance(PATH_TO_FILE, "instance30_A=5_H=4_cf=ndcs.json")

    logging.info(f" Instance: n={len(A)}, h={len(H)}")
    tracemalloc.start()
    start_time = time.time()    
    FCSS_star = sdp(A, H, Pi, G_R_2)
    logging.info(f' elapsed time (s): {time.time()-start_time}')
    current, peak = tracemalloc.get_traced_memory()
    logging.info(f" current memory usage is {current / 10**6}MB; peak was {peak / 10**6}MB")
    tracemalloc.stop()

    logging.info(f'Total Value = {FCSS_star["v"]}')
    for v, CS in FCSS_star['h']:
        logging.info(f'V({CS}) = {v}')    