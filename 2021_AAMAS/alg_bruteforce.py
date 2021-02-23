import os, sys; sys.path.append(os.path.dirname(os.path.realpath(__file__)))
import itertools
from gen_input import gen_A, gen_H

def partition(collection):
    if len(collection) == 1:
        yield [frozenset(collection)]
        return
    first = collection[0]
    for smaller in partition(collection[1:]):
        for n, subset in enumerate(smaller):
            yield smaller[:n] + [subset.union(frozenset([first]))]  + smaller[n+1:]
        yield [frozenset([first])] + smaller

def next_CS(CS, n, length, reflexive=True):
    partitions = []
    for C in CS:
        partitions.append(partition(list(C)))
    for p in itertools.product(*partitions):  
        CS_prime = list(itertools.chain(*p))
        if not reflexive and len(CS_prime) == len(CS): continue
        if n-len(CS_prime) < length-1: continue
        yield frozenset(CS_prime)

def v_cs(v, CS):
    # return sum([v[C] for C in CS])
    return sum([v(C) for C in CS])
def v_fcss(H, FCSS):
    return sum([v_cs(H[i], CS) for i, (v, CS) in enumerate(FCSS)])

def bruteforce(A, H, R):
    FCSS_star = {'v':0, 'h':[(0, {})]}
    for CS in map(frozenset, partition(A)):  
        if len(CS) <= len(A) - (len(H)-1): 
            bruteforce_sequence(len(A), [(v_cs(H[0], CS), CS)], H, FCSS_star)
    return FCSS_star
def bruteforce_sequence(n, FCSS, H, FCSS_star):
    if len(FCSS) >= len(H):
        if v_fcss(H, FCSS) > FCSS_star['v']:
            FCSS_star['v'] = v_fcss(H, FCSS)
            FCSS_star['h'] = FCSS
        return     
    for CS_prime in next_CS(FCSS[-1][1], n, len(H)-len(FCSS), reflexive=False):
        if n-len(CS_prime) >= len(H)-(len(FCSS)+1): 
            bruteforce_sequence(n, FCSS+[(v_cs(H[len(FCSS)],CS_prime), CS_prime)], H, FCSS_star)
    return

if __name__ == "__main__":
    import logging
    import time
    import numpy as np
    logging.basicConfig(level=logging.DEBUG)
    logging.info("Brute-force Algorithm for Relation R_S")

    n = 4
    h = 3
    A = gen_A(n)
    H = gen_H(A, h, lambda c: np.random.normal(len(c), len(c)))

    logging.info(f" Instance: n={len(A)}, h={len(H)}")
    start_time = time.time()
    FCSS_star = bruteforce(A, H, lambda:x)
    logging.info(f' elapsed time (s): {time.time()-start_time}')

    logging.info(f' Total Value = {FCSS_star["v"]}')
    for v, CS in FCSS_star['h']:
        logging.info(f' V({CS}) = {v}')