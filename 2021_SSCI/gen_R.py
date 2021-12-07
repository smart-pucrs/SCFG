import os, sys; sys.path.append(os.path.dirname(os.path.realpath(__file__)))
import itertools

def partition(collection):
    if len(collection) == 1:
        yield [ collection ]
        return
    first = collection[0]
    for smaller in partition(collection[1:]):
        for n, subset in enumerate(smaller):
            yield smaller[:n] + [[ first ] + subset]  + smaller[n+1:]
        yield [ [ first ] ] + smaller
def partition_k(collection, k):
    def partition(collection, n, k):
        if k == 1:
            yield [collection]
            return
        if len(collection) == 1:
            yield [ collection ]
            return
        first = collection[0]
        for smaller in partition(collection[1:], n, k):
            b = k-(len(collection)-2)
            if len(smaller) == k:
                for i, subset in enumerate(smaller):
                    yield smaller[:i] + [[ first ] + subset]  + smaller[i+1:]   
            elif len(smaller) < k:
                if len(collection) < n:
                    for i, subset in enumerate(smaller):
                        yield smaller[:i] + [[ first ] + subset]  + smaller[i+1:]
                    yield [ [ first ] ] + smaller  
                elif len(smaller) == k-1:
                    yield [ [ first ] ] + smaller  
    yield from partition(collection, len(collection), k)

def R_H(index, CS, FCS):
    fcs = [cs for i, cs in enumerate(FCS) if i!= index and cs!=[]]
    for cs in fcs:
        for c in CS:
            b = [len(c.intersection(temp)) <= 1 for temp in cs]
            if not all(b):
                return False
    return True
def R_S(index, CStemp, FCS):
    def check_R_S(CS, FCS):
        if len(FCS) == 0: return True
        if len(CS) >= len(FCS[0]): return False
        for c_prime in FCS[0]:
            b = [c_prime <= c for c in CS]
            if not any(b):
                return False
        return check_R_S(FCS[0], FCS[1:])
    return check_R_S(FCS[0], FCS[1:])   
def R_S(FCS, CS):
    for CS_prime in FCS:
        if len(CS_prime) >= len(CS): return False
        for C in CS:
            b = [C <= C_prime for C_prime in CS_prime]
            if not any(b):
                return False
    return True 

def G_R_1(A, h, CS):
    if len(CS) == 0:
        for CS_prime in partition(A):
            yield frozenset(list(map(frozenset, CS_prime)))
    else:
        done = False
        for l_CS_prime in partition(A):
            if done:
                yield frozenset(list(map(frozenset, l_CS_prime)))
            else:                
                CS_prime = frozenset(list(map(frozenset, l_CS_prime)))
                if CS == CS_prime:
                    done = True
                else:
                    yield CS_prime
def V_R_1(CS, CS_prime):
    return not CS == CS_prime

def G_R_2(A, h, CS):
    if len(CS) == 0:
        for CS_prime in partition(A):
            yield frozenset(list(map(frozenset, CS_prime)))
    else:
        for CS_prime in partition_k(A, len(CS)):
            yield frozenset(list(map(frozenset, CS_prime)))
def V_R_2(CS, CS_prime):
    if len(CS) == 0:
        return True
    return len(CS) == len(CS_prime)

def G_R_3(A, h, CS):
    if len(CS) == 0:
        for l_CS in partition(A):
            if len(l_CS) <= len(A) - (h-1):
                yield frozenset(list(map(frozenset, l_CS)))
    else:
        CS_prime = CS
        partitions = []
        for C_prime in CS_prime:
            partitions.append(partition(list(C_prime)))
        for p in itertools.product(*partitions):  
            new_cs = list(itertools.chain(*p))
            if len(new_cs) == len(CS_prime): continue
            yield frozenset(map(frozenset, new_cs))
def V_R_3(CS, CS_prime):
    if len(CS) == 0:
        return True 
    if len(CS) == len(CS_prime):
        return False 
    for c in CS_prime:
        b = [c <= temp for temp in CS]
        if not any(b):
            return False
    return True

def G_R_4(A, h, CS):
    if len(CS) == 0:
        for CS_prime in partition(A):
            yield frozenset(list(map(frozenset, CS_prime)))
    else:
        yield CS.copy()
def V_R_4(CS, CS_prime):
    if len(CS) == 0:
        return True
    if len(CS) != len(CS_prime):
        return False
    for C in CS:
        equal = False
        for C_prime in CS_prime:
            if C == C_prime:
                equal = True
        if not equal:
            return False
    return True
