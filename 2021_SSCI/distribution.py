import math
import numpy as np
from collections import defaultdict
from random import randint

def uniform(c):
    return np.random.uniform(0, len(c))

def modified_uniform(c):
    val = np.random.uniform(0, 10*len(c))
    if randint(1,100) <= 20:
        val += np.random.uniform(0, 50)
    return val

table_ag_u = {}
def agent_based_uniform(c):
    global table_ag_u
    return sum(map(lambda ag: np.random.uniform(0, 2*table_ag_u[ag]), c))

def normal(c):
    return np.random.normal(10*len(c), 0.01)

def modified_normal(c):
    val = np.random.normal(10*len(c), 0.01)
    if randint(1,100) <= 20:
        val += np.random.uniform(0, 50)
    return val

table_ag_n = {}
def agent_based_normal(c):
    global table_ag_n
    return sum(map(lambda ag: np.random.normal(table_ag_n[ag], 0.01), c))

def ndcs(c):
    return np.random.normal(len(c), len(c))

def exponential(c):
    return len(c)*np.random.exponential(1)

def beta(c):
    return len(c)*np.random.beta(0.5,0.5)

def gamma(c):
    return len(c)*np.random.gamma(2,2)

def reset():
    global table_ag_u, table_ag_n
    table_ag_u = defaultdict(lambda: np.random.uniform(0, 10))
    table_ag_n = defaultdict(lambda: np.random.normal(10, 0.01))

all_functions = [uniform, modified_uniform, agent_based_uniform, normal, modified_normal, agent_based_normal, ndcs, exponential, beta, gamma] 