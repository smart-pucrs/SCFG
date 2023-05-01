import os
import logging
import networkx as nx
import numpy as np
import math
import signal as sig
import time
from collections import defaultdict

from gen_R import GenCS
from seqsvs_vs import check_SVS, cf_v, V_cs, V_seq
from structure import Node, Alg, alg
from procedure_merge_split import split, merge

class Timeout(Exception): pass
timeout_fired = False
def signal_handler(signum, frame):
    global timeout_fired
    # raise Timeout("Timed out!")
    timeout_fired = True

table_actions = dict()

def create_X_level(CS, level):
    global table_actions
    if CS not in table_actions:
        table_actions[CS] = {'a': [], 'gl': {i: GenCS(CS, alg.R, alg.H[i], 5, alg.Pi[i][0], alg.Pi[i][1], alg.Pi[i][2]) for i in range(len(alg.H))}}

def add_to_table(key, value, level=0):
    global table_actions
    create_X_level(key, level)
    action = table_actions[key]
    
    if value not in action['a']:
        action['a'].append(value)

class Expanded(Exception): pass
def retrieve_action(node, position):
    next_level = node.level+1

    create_X_level(node.CS, next_level) 

    if position < len(table_actions[node.CS]['a']):
        return table_actions[node.CS]['a'][position]
    else: 
        if table_actions[node.CS]['gl'][next_level] == None:
            raise Expanded
        try:
            CS = next(table_actions[node.CS]['gl'][next_level])
            if CS != None:
                add_to_table(node.CS, CS, level=next_level)              
                return CS
        except (StopIteration) as e:
            table_actions[node.CS]['gl'][next_level] = None
    return None

def progressive_widening(node):   
    try:
        CS = retrieve_action(node, node.last)
        if CS != None:
            node.last += 1
            if not check_SVS(CS, alg.Pi[node.level+1][0], alg.Pi[node.level+1][1], alg.Pi[node.level+1][2]):
                return
            add_frontier(node, getNode(CS, node))
    except (Expanded) as e:
        node.expanded = True
        if len(node.frontier)==0:
            node.terminal = True

    return

def add_frontier(parent, child, expanded=False):
    for e in parent.frontier+parent.done:
        if e.CS == child.CS:
            return
    parent.frontier.append(child)

def getNode(CS, parent=None):
    level = parent.level+1 if parent != None else -1
    node = Node(parent=parent, CS=CS, v=V_cs(CS, alg.H[level]), level=level, data=alg)
    if node.level == alg.h-1:
        node.terminal = True
    return node

def priority(parent, child):
    C = math.sqrt(2)
    if child.N == 0: 
        return child.v + (C * math.sqrt(math.log(parent.N+1, math.e)))
    else:
        return (child.cumv/(child.N)) + (C * math.sqrt(math.log(parent.N, math.e)/child.N))

def calc(node):
    return node.vp 

def selection(parent):
    chosens = [parent.frontier[0]]

    value = priority(parent, parent.frontier[0])

    parent.frontier[0].pr = value

    for i, node in enumerate(parent.frontier[1:], start=1):
        node.pr = priority(parent, node)

        if value < node.pr:
            value = priority(parent, node)
            chosens = [node]
        elif value == node.pr:
            chosens.append(node)

    if len(chosens) > 1:
        i = np.random.randint(0, len(chosens))
        chosen = chosens[i]
    else:
        chosen = chosens[0]

    return chosen, None   

def should_expand(branch):
    return math.pow(branch.N, alg.exp_factor) >= len(branch.frontier)  # value represents the chance of expanding the frontier

def rollout(CS, level, alg, max_depth=np.infty,  max_degree=np.infty):
    if level == max_depth: 
        return sum([cf_v(C, alg.H[level]) for C in CS]), True
    
    reward, completed = -np.infty, False

    CS_prime = split(CS, None, alg.Pi[level+1][0], {frozenset([s]) for s in alg.Pi[level+1][1]}, maxsize=max(alg.Pi[level+1][2]))
    if alg.R(CS, CS_prime):
        add_to_table(CS, CS_prime, level=level+1)

        if check_SVS(CS_prime, alg.Pi[level+1][0], alg.Pi[level+1][1], alg.Pi[level+1][2]):   
            reward, completed = rollout(CS_prime, level+1, alg, max_depth=max_depth, max_degree=max_degree)  

    for i in range(max_degree+1): 
        if completed:
            break

        CS_prime = merge(CS, CS_prime, None, alg.R, alg.Pi[level+1][0], alg.Pi[level+1][1], maxsize=alg.Pi[level+1][2], add_function=add_to_table, level=level+1)
        if CS_prime == None:
            break           

        reward_prime, completed = rollout(CS_prime, level+1, alg, max_depth=max_depth, max_degree=max_degree)  

        reward = max(reward, reward_prime)        

    if reward == -np.infty:
        reward = 0

    return sum([cf_v(C, alg.H[level]) for C in CS]) + reward, completed

def tree_policy(parent):
    if parent.terminal:
        return parent
    
    if not parent.expanded and should_expand(parent):
        progressive_widening(parent)
    
    if len(parent.frontier) > 0:
        node, _ = selection(parent)   

        if node.N == 0:
            return node
        
        return tree_policy(node)
    return parent

def default_policy(node):
    if node.N > 0:
        return 0
    
    if node.terminal:
        if node.level == alg.h-1:
            return node.v
        
        return 0 
    
    desired_depth = min(node.level+alg.depth, alg.h-1)

    reward, _ = rollout(node.CS, node.level, alg, max_depth=desired_depth, max_degree=alg.degree)

    return reward

def update(node, reward, length, force_update, path=[]):
    node.N += 1
    node.cumv += reward

    if node.parent != None:    
        update(node.parent, reward, length, force_update, [node]+path)

def retrieve_FCSS(node):
    FCSS = []
    while node.parent != None:
        FCSS.append(node.CS)
        node = node.parent

    return list(reversed(FCSS))

def remove(node):
    node.parent.frontier.remove(node)
    node.parent.done.append(node)
    if len(node.parent.frontier)==0 and node.parent.expanded:
        node.parent.terminal = True

def feasible_CSS(CSS, R):
    for i in range(len(CSS)):
        CS_prime = {} if i==0 else CSS[i-1] 
        if not R(CS_prime, CSS[i]) or not check_SVS(CSS[i], alg.Pi[i][0], alg.Pi[i][1], alg.Pi[i][2]):
            return False
    return True

def save_FCSS(folder, FCSS):
    if not os.path.exists(folder):
        os.makedirs(folder)

    import jsonpickle
    import datetime

    id = len([name for name in os.listdir(folder)])
    timestr = datetime.datetime.utcnow().strftime("%Y%m%d-%H:%M:%S.%f")

    f = open(f"{folder}/FCSS_{id+1}_{timestr}.json","w")   
    f.write(jsonpickle.encode(FCSS,make_refs=False))
    f.close()

best_length = 0
total_nodes = 0
def MCTS(A, H, Pi, R, start_time, degree=5, depth=3, gamma=.25, end_time=60, aimed_value=-np.infty, first_after_timeout=False, folder_result=''):
    global alg, best_length, total_nodes, table_actions, timeout_fired
    del alg 
    del table_actions

    timeout_fired = False
    table_actions = defaultdict(lambda: {'a': [], 'l':0})

    alg = Alg(A=A, H=H, R=R, Pi=Pi, degree=degree, depth=depth, exp_factor=gamma)

    logging.info(f"parameters: degree={degree} depth={depth} gamma={gamma} time={end_time}")

    FCSS_star = {'v': -np.infty, 'h': [(0, {}) for i in range(len(H))]}  
    intermediary_results = []
    FCSS_found = []
    root = getNode(frozenset([]))

    sig.signal(sig.SIGALRM, signal_handler)
    sig.alarm(end_time)   # in seconds   

    best_length = 0
    total_nodes = 0
    force_termination = return_first = False
    
    while not root.terminal and not force_termination:
        node = tree_policy(root)

        if best_length<node.level+1:
            best_length=node.level+1
            print(f"length: {best_length} took: {time.time()-start_time}")

        if len(node.CS)==0:
            continue

        reward = default_policy(node)   

        update(node, reward, node.length-1, False)

        if node.terminal:
            if node.level == alg.h-1:
                found_time = time.time()-start_time       
                FCSS = retrieve_FCSS(node)
                if V_seq(FCSS, H) > FCSS_star['v']:
                    if not feasible_CSS(FCSS, alg.R):
                        for i, CS in enumerate(FCSS):
                            logging.info(f'V({CS}) = {V_cs(CS, alg.H[i])}')   

                    FCSS_star['v'] = V_seq(FCSS, H) 
                    FCSS_star['h'] = [(sum([cf_v(C,H[i]) for C in cs]), cs) for i, cs in enumerate(FCSS)]  

                    intermediary_results.append((FCSS_star['v'], found_time))

                    save_FCSS(folder_result, FCSS)

                    logging.info(f"{root.N} New FCCS* {FCSS_star['v']}, it took (s): {found_time}")
 
                    if return_first:
                        force_termination = True  
                FCSS_found.append((FCSS_star['v'], found_time)) 
            remove(node)

        if timeout_fired:  
            timeout_fired = False      
            if first_after_timeout and FCSS_star['v'] == -np.infty:
                return_first = True
            else:
                force_termination = True
                
    sig.alarm(0)

    return FCSS_star, intermediary_results, FCSS_found

def convert_graphs(Pi):
    for i, vs in enumerate(Pi):
        G, new_G = vs[0], nx.Graph()

        for n in G.nodes():
            new_G.add_node(frozenset([n]))

        for u, v in G.edges():
            new_G.add_edge(frozenset([u]),frozenset([v]), color='green')

        Pi[i] = (new_G, vs[1], vs[2], vs[3], vs[4], vs[5],  vs[6])
