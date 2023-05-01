import scipy.stats as sp
import math

rrf = None
upsidedown = False

def compute_roles(C, level, hybrid, debug=False):
    if debug: print(f"... {level} {C}")

    counter_roles = dict()

    index = 0 if upsidedown else -1

    if debug: print(f"..... ag {index} {C.intersection(rrf.Pi[index][1])}")

    for s in C.intersection(rrf.Pi[index][1]):
        for r in rrf.get_expect_roles(s):
            val = counter_roles.get(r, 0)
            counter_roles[r] = val + 1

    C_prime = C.difference(rrf.L)    

    coalition_roles = {r:0 for r in counter_roles}

    for ag in C_prime:
        for r in rrf.get_roles(ag):
            if hybrid and len(counter_roles) == 0:                
                coalition_roles[r] = coalition_roles.get(r, 0) + 1
                continue
                
            if r in counter_roles: # from the first relative level
                coalition_roles[r] += 1
    
    if debug: print(f".....counter roles {counter_roles}")
    if debug: print(f".....counter coalition {dict(coalition_roles)}")

    return counter_roles, coalition_roles

def disturbance_entropy(C, level, hybrid, debug=False):   
    required_roles, roles_in_coalition = compute_roles(C, level, debug)

    if hybrid:
        if len(roles_in_coalition) == 1:
            return 0
        
        total_p = sum(roles_in_coalition.values())
        if total_p == 0: # coalition has only a superior
            return 1
        
        p = [v/total_p for v in roles_in_coalition.values()]

        entropy = 1 - sp.entropy(pk=p) / math.log(len(p))
    else:
        if len(required_roles)==1:
            return 0
        
        if  len(required_roles)==0 or len(roles_in_coalition) == 0:
            return 1 
        
        list_of_roles = required_roles.keys()

        total_p, total_q = sum(roles_in_coalition.values()), sum(required_roles.values())

        if total_p == 0:
            return 1
        
        q = [required_roles[r]/total_q for r in list_of_roles]
        p = [roles_in_coalition.get(r, 0)/total_p for r in list_of_roles]

        entropy = sp.entropy(pk=p, qk=q) / math.log(len(q))

    if debug: print(f".....entropy {entropy}")

    return entropy

def relationship(C, level, hybrid, debug=False):
    if len(C) == 1: 
        return 0
    
    value, samples = 0, 0
    
    if hybrid:
        C_prime = C
        l_C = list(C)
        for i, a1 in enumerate(l_C):        
            for a2 in l_C[i+1:]:         
                value += rrf.get_rel(a1, a2)
                samples += 1
    else:
        pivotal_agents = C.intersection(rrf.Pi[level][1])

        if len(pivotal_agents) == 0: 
            if debug: print(f"....no superior to compute relationship")
            return 0

        C_prime = C.difference(pivotal_agents)

        for p in pivotal_agents:        
            for ag in C_prime:         
                value += rrf.get_rel(p, ag)
                samples += 1
    
    if debug: print(f"....relationship {value} {samples} {len(C_prime)}")

    return value / samples
    
def v_1(C, level, hybrid=False, debug=False): 
    entropy = disturbance_entropy(C, level, hybrid, debug)  
    relation = relationship(C, level, hybrid, debug)   

    return len(C) * (relation - entropy)
