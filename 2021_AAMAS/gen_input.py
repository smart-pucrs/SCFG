import os, sys; sys.path.append(os.path.dirname(os.path.realpath(__file__)))
import itertools

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