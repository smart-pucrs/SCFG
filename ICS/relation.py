from collections import defaultdict
from collections import Counter

_instance = None
def initiliase(instance):
    global _instance
    _instance = instance

def sub_inv_R_ICS(CS, CS_prime): 
    if len(CS) == 0:
        for C_prime in CS_prime:
            if len(C_prime) > _instance.span_of_control+1:
                return False 
    else:
        if len(CS) == len(CS_prime):
            return False 
        
        count_soc = defaultdict(lambda: 0)
        for C in CS:
            is_subset = False
            for C_prime in CS_prime:
                if C_prime >= C:
                    is_subset = True
                    count_soc[C_prime] += 1
                    break

            if not is_subset: 
                return False
            
        if max(count_soc.values()) > _instance.span_of_control+1:
            return False    
    return True

def sub_inv_R_ICS_hybrid(CS, CS_prime):
    if len(CS) == 0:
        for C_prime in CS_prime:
            if len(C_prime) > _instance.span_of_control+1:
                return False 
    else:
        if len(CS) == len(CS_prime):
            return False 
        
        count_soc = defaultdict(lambda: 0)
        count_superiors = defaultdict(lambda: 0)
        for C in CS:
            is_subset = False
            for C_prime in CS_prime:                
                if C_prime >= C:
                    is_subset = True
                    if len(C)==1 and len(C.intersection(_instance.L))>0:
                        count_superiors[C_prime] += 1
                    else:
                        count_soc[C_prime] += 1
                    break
            if not is_subset: 
                return False
            
        if max(count_soc.values()) > _instance.span_of_control:
            return False   
        
        if max(dict(Counter(count_soc)+Counter(count_superiors)).values()) > _instance.span_of_control+1:
            return False
    return True
