import os, sys

from numpy.lib.function_base import select; sys.path.append(os.path.dirname(os.path.realpath(__file__)))
import numpy as np
import networkx as nx
import math
import random 
import yaml
from collections import defaultdict
import json

PATH_DIR = os.path.dirname(os.path.realpath(__file__))

class RRF():
    def __init__(self, setOfAgents, constraints, span_of_control) -> None:
        self.span_of_control = span_of_control
        self._agents = setOfAgents
        self._L = {e for e, info in setOfAgents.items() if info['leader']}     
        self._H = []
        self._structures = constraints
        self._relationship = dict()

    @property
    def A(self):
        return list(self._agents.keys())
    @property
    def L(self):
        return self._L
    @property
    def H(self):
        return self._H
    @property
    def Pi(self):
        return [(s['graph'],s['pivotal'],s['size']) for s in self._structures]
    
    def get_agents(self):
        return self._agents
    
    def get_expect_roles(self, agent):
        if self._agents[agent]['leader'] == False:
            return set()
        return self._agents[agent]['expect']
    
    def get_roles(self, agent):
        return self._agents[agent]['adopt']

    def get_rel(self, ag1, ag2):
        edge = sorted([ag1, ag2])
        return self._relationship[edge[0]][edge[1]]  
    
    def set_rel(self, ag1, ag2, val):
        if ag1 == ag2: return

        edge = sorted([ag1, ag2])

        if edge[0] not in self._relationship:
            self._relationship[edge[0]] = {}

        self._relationship[edge[0]][edge[1]] = val    

    def set_all_rel(self, rel):
        self._relationship = rel

    def set_cf(self, index, f_real):
        self._H[index] = f_real

    def save_instance(self, path_to_file, max_number_of_roles_to_adopt):
        from networkx.readwrite import json_graph
        import jsonpickle
        info = {}
        info['span'] = self.span_of_control
        info['agents'] = jsonpickle.encode(dict(self._agents))
        info['structures'] = []
        for e in self._structures:
            structure = jsonpickle.encode(json_graph.adjacency_data(e['graph'])), jsonpickle.encode(e['pivotal']), jsonpickle.encode(e['size']) 
            info['structures'].append(structure)
        info['relationship'] = jsonpickle.encode(self._relationship)

        f = open(f"{path_to_file}/RRF_A={len(self.A)}_adopt={max_number_of_roles_to_adopt}_H={len(self._structures)}.json","w")
        
        f.write(json.dumps(info))
        f.close()

    def make_it_hybrid(self, goals=""):
        goals = RRF.load_object(goals)
        progressive_pivotal = set()
        l_A = self.A
        for structure in self._structures:
            iG = structure["graph"]      
            progressive_pivotal.update(structure['pivotal'])
            for j, a1 in enumerate(l_A):
                if a1 in progressive_pivotal: continue
                connect_to_roles = {r for g, info in goals.items() if len(self._agents[a1]['adopt'].intersection(info['roles']))>0 for r in info['roles']} 
                for a2 in l_A[j+1:]:
                    if a2 in self.L: continue
                    if a1 in self.L:
                        if len(self._agents[a2]['adopt'].intersection(self._agents[a1]['expect'])) > 0:
                            iG.add_edge(frozenset([a1]), frozenset([a2]), color="green") 
                    else:
                        if len(self._agents[a2]['adopt'].intersection(connect_to_roles))>0:
                            iG.add_edge(frozenset([a1]), frozenset([a2]), color="green")

    def add_chief(self, upsidedown=False):
        chief = 'a0'
        # fourth game
        structure_chief = {"graph": None, "pivotal": set([chief]), "size": set()}
        iG = nx.Graph()
        for a in self.A:
            self.set_rel(chief, a, 0)
            iG.add_edge(frozenset([chief]), frozenset([a]))

        self._agents[chief] = {"kind": "personnel", "leader": True, 'level': 0, 'expect': set(), 'independent': set(), 'goals': set(), 'adopt': set()}
        self._L.add(chief)
        structure_chief['graph'] = iG
        structure_chief['size'] = {len(self._agents)}

        # add chief other games
        for structure in self._structures:
            structure["graph"].add_node(frozenset([chief]))  

        if upsidedown:
            self._structures.insert(0,structure_chief)
            self._H.insert(0,[])
        else:
            self._structures.append(structure_chief)
            self._H.append([])    

    @classmethod
    def save_relationship(cls, path_to_file, n, relationship):
        import jsonpickle
        info = {}        
        info['relationship'] = jsonpickle.encode(relationship)

        f = open(f"{path_to_file}/RRF_relationship_A={n}.json","w")
        
        f.write(json.dumps(info))
        f.close()

    @classmethod
    def generate_set_agents(cls, n, span_of_control, max_number_of_roles=3, hierarchy_specification="", roles="", goals=""):
        roles = RRF.load_object(roles) 
        goals = RRF.load_object(goals)
        hierarchy_specification = RRF.load_object(hierarchy_specification)

        required_roles = set()
        max_roles = defaultdict(lambda: 0)
        n_L = 0
        for C in hierarchy_specification:
            n_L += C['quantity']
            if C['level']==2:
                expect_roles = {role for g in C['goals'] for role in goals[g]['roles']}
                required_roles.update(expect_roles)
                for r in expect_roles:
                    max_roles[r] += math.ceil(span_of_control/len(expect_roles)) * C['quantity'] 
        b = sum(max_roles.values()) + n_L
        prob_roles = [max_roles[k]/sum(max_roles.values()) for k in max_roles.keys() if k in max_roles]
        a = sum(prob_roles)
        set_of_agents = defaultdict(lambda: {"adopt": [], "kICS": 1, "leader": False})
        
        roles = {k:v for k, v in roles.items() if k in required_roles}
        roles_personnel = [k for k, v in roles.items() if v['kind']=='personnel']
        roles_team = [k for k, v in roles.items() if v['kind']=='team']
        i = 0
        for C in hierarchy_specification:
            for _ in range(C['quantity']):
                i += 1
                set_of_agents["a"+str(i)]["kind"] = "personnel"
                set_of_agents["a"+str(i)]["leader"] = True
                set_of_agents["a"+str(i)]['level'] = C['level']
                set_of_agents["a"+str(i)]['expect'] = set()
                set_of_agents["a"+str(i)]['independent'] = set()
                for g in C['goals']:
                    set_of_agents["a"+str(i)]['expect'].update(goals[g]['roles'])
                    set_of_agents["a"+str(i)]['independent'].add(frozenset(goals[g]['roles']))
                set_of_agents["a"+str(i)]["adopt"] = set(np.random.choice(roles_personnel, 1))    

        # MANY ROLES
        prob_personnel = [max_roles[k]/sum([v for r, v in max_roles.items() if r in roles_personnel]) for k in roles_personnel]
        prob_team = [max_roles[k]/sum([v for r, v in max_roles.items() if r in roles_team]) for k in roles_team]
        for k, v in roles.items():
            i += 1
            if v['kind'] == 'personnel':
                number_of_roles = random.randint(1, max_number_of_roles)
                aux = np.random.choice(roles_personnel, number_of_roles-1,replace=False, p=prob_personnel)
                set_of_agents["a"+str(i)]['adopt'] = set([*aux, k])
                set_of_agents["a"+str(i)]["kind"] = v["kind"]  
            else:
                set_of_agents["a"+str(i)]['adopt'] = {k}
                set_of_agents["a"+str(i)]["kind"] = v["kind"]     

        chance_of_personnel = (len(roles_personnel)/(len(roles_personnel)+len(roles_team)))
        for i in range(n_L+len(roles)+1,n+1):
            if np.random.uniform(0,1) <= chance_of_personnel:
                number_of_roles = random.randint(1, max_number_of_roles)
                role = np.random.choice(roles_personnel, number_of_roles,replace=False, p=prob_personnel)
                set_of_agents["a"+str(i)]['adopt'] = set([*role])
                set_of_agents["a"+str(i)]["kind"] = roles[role[0]]['kind']
            else:
                role = np.random.choice(roles_team, 1,replace=False, p=prob_team)[0]
                set_of_agents["a"+str(i)]['adopt'] = set([role])
                set_of_agents["a"+str(i)]["kind"] = roles[role]['kind']

        # # TO BE THE PRECISE NUMBER
        # leaders = list(filter(lambda v: v['level']==2, set_of_agents.values()))
        # for p  in leaders:
        #     get_roles = itertools.cycle(p['expect'])
        #     for count in range(soc):
        #         i += 1
        #         chosen_role = next(get_roles)
        #         set_of_agents["a"+str(i)]['adopt'] = set([chosen_role])
        #         set_of_agents["a"+str(i)]["kind"] = roles[chosen_role]['kind']

        return set_of_agents

    @classmethod
    def generate_constraints(self, A, h, span_of_control):      
        from datetime import datetime
        np.random.seed(np.int64(datetime.utcnow().timestamp()))     
        l_A = list(A.keys())
        structures = []
        superiors = {k for k, v in A.items() if v.get('level', -1) != -1}
        stay_in_singletons = []
        progressive_pivotal = set()
        for i in range(h):
            structure = {"graph": None, "pivotal": set(), "size": set()}
            iG = nx.Graph()
            iG.add_nodes_from([frozenset([a]) for a in A])
      
            structure['pivotal'] = {k for k, v in A.items() if v.get('level', -1) == i}
            progressive_pivotal.update(structure['pivotal'])
            if i == h-1:
                structure['size'] = set(range(1, span_of_control+1+1))
            else:
                structure['size'] = set(range(1, len(A)+1))
   
            # FIXED HIERARCHY
            for a1 in structure['pivotal']:
                for a2 in A.keys():
                    if a1 != a2 and a2 not in stay_in_singletons and a2 not in structure['pivotal']:
                        # if len(A[a2]['adopt'].intersection(A[a1]['expect'])) > 0:
                        #     iG.add_edge(frozenset([a1]), frozenset([a2]), color="green") 
                        if a2 in superiors:
                            # if len(A[a2]['expect'].intersection(A[a1]['expect'])) > 0:
                            # if A[a2]['expect'].issubset(A[a1]['expect']):
                            if A[a2]['independent'].issubset(A[a1]['independent']):
                                iG.add_edge(frozenset([a1]), frozenset([a2]), color="green")
                        else:
                            if len(A[a2]['adopt'].intersection(A[a1]['expect'])) > 0:
                                iG.add_edge(frozenset([a1]), frozenset([a2]), color="green") 

            structure['graph'] = iG
            stay_in_singletons.extend(list(structure['pivotal']))
            structures.append(structure)
        return structures

    @classmethod
    def load_object(cls, full_path):
        obj = {}
        with open(PATH_DIR+full_path, 'r') as file:
            obj = yaml.safe_load(file)
        return obj
   
    @classmethod
    def load_instance(cls, path_to_file, file_name, file_relationship):
        import jsonpickle
        from networkx.readwrite import json_graph

        info = None
        with open(f"{path_to_file}/{file_name}.json", 'r+') as _file:
            info = jsonpickle.decode(_file.read())
        
        setOfAgents = jsonpickle.decode(info['agents'])
        constraints = []
        for structure in info['structures']:
            ctr = {'graph': {}, 'pivotal': {}, 'absent': set()}
            ctr['graph'] = json_graph.adjacency_graph(jsonpickle.decode(structure[0]))
            ctr['pivotal'] = jsonpickle.decode(structure[1])
            ctr['size'] = jsonpickle.decode(structure[2])
            constraints.append(ctr)
            
        instance = RRF(setOfAgents, constraints, span_of_control=info['span'])
        instance._H = [0] * len(instance._structures)

        with open(f"{path_to_file}/{file_relationship}.json", 'r+') as _file:
            info = jsonpickle.decode(_file.read())

        instance.set_all_rel(jsonpickle.decode(info['relationship']))

        return instance

def compute_roles(instance):
    agents = instance.get_agents()
    c_roles = defaultdict(lambda: 0)
    c_leader_roles = defaultdict(lambda: 0)
    c_leader_roles_abs = defaultdict(lambda: 0)

    for _, desc in agents.items():
        if desc['leader'] == False:
            for r in desc['adopt']:
                c_roles[r] += 1
        else:
            c_roles[0] += 1
            c_leader_roles[0] += 1
            c_leader_roles_abs[0] += 1
            if desc['level'] == 2:
                for r in desc['expect']:
                    c_leader_roles[r] += 1
                    c_leader_roles_abs[r] += math.ceil(instance.span_of_control/len(desc['expect'])) 
    return c_roles, c_leader_roles, c_leader_roles_abs