import os, sys; sys.path.append(os.path.dirname(os.path.realpath(__file__)))
import itertools
import logging
import math
import time
import tracemalloc
import pandas as pd 
import signal as sig
from natsort import natsorted

from gen_seqvs_input import load_instance
from distribution import *
from gen_R import G_R_1, G_R_2, G_R_3, G_R_4, V_R_1, V_R_2, V_R_3, V_R_4
from alg_sdp import sdp
from alg_bruteforce import bruteforce
from alg_mclink_seqvs import mclink


from importlib import reload
reload(logging)

WORKING_DIR = os.path.dirname(os.path.realpath(__file__))
logging.basicConfig(filename=WORKING_DIR+'/h_debug.log', filemode='w', level=logging.DEBUG)
exp_logger = logging.getLogger()

class TimeoutException(Exception): pass
def signal_handler(signum, frame):
    exp_logger.info(f" timeout here")
    raise TimeoutException("Timed out!")

def powerset(iterable):
    s = list(iterable)
    return itertools.chain.from_iterable(itertools.combinations(s, r) for r in range(len(s)+1))

if __name__ == "__main__":
    exp_logger.info("Evaluating Different Algorithms on the Same Problem Instance")
    exp_logger.info(f"   {time.asctime(time.localtime(time.time()))}")

    
    columns = ['|A|', 'Alg', 'h', 'cf', 'R', 'value', 'time', 'memory', 'edges', 'pivotals']
    df = pd.DataFrame([], columns = columns) 
    file_name = f'{WORKING_DIR}/comparing_algs.csv'
    df.to_csv(file_name, index=False)
    del df

    max_ag = 4
    algorithms = [bruteforce, sdp, mclink]
    Rs_G = [(G_R_1,'R_1'), (G_R_2,'R_2'), (G_R_3,'R_3'), (G_R_4,'R_4')]  
    Rs_V = [(V_R_1,'R_1'), (V_R_2,'R_2'), (V_R_3,'R_3'), (V_R_4,'R_4')]      
    cfs = [ndcs]
    range_A = range(2, max_ag+1)

    TIMEOUT = 60*60 # in seconds
    TIMEOUT_VALUE = math.inf
    CSS_timeout = {'v':TIMEOUT_VALUE, 'h':[(0, {})]}

    PATH_TO_FILE = WORKING_DIR+"/instances"
    files = [filenames for (_,_,filenames) in os.walk(PATH_TO_FILE)] 

    for file in natsorted(files[0]): 
        cf = file[file.index("cf=")+3:file.index(".json") ]
        A, H, Pi = load_instance(PATH_TO_FILE, file)
        exp_logger.info(f'For A={len(A)} H={len(H)} cf={cf}')
        print(f'For A={len(A)} H={len(H)} cf={cf}')

        for alg in algorithms: 
            exp_logger.info(f'Running {alg.__name__}') 
            print(f'..running {alg.__name__}')
            exp_R = Rs_V if alg.__name__=='mclink' else Rs_G    
            results = pd.DataFrame([], columns = columns)                                   
            for R, R_name in exp_R:                                      
                exp_logger.info(f'R: {R_name}')  
                print(f'....{R.__name__} {time.asctime(time.localtime(time.time()))}')
                exp_logger.info(f"   {time.asctime(time.localtime(time.time()))}")
                sig.signal(sig.SIGALRM, signal_handler)
                sig.alarm(TIMEOUT)   # in seconds   
                try:
                    tracemalloc.start()
                    start_time = time.time()
                    FCSS = alg(A, H, Pi, R)                                  
                    end_time = time.time()                        
                    sig.alarm(0)                                
                    mem_current, mem_peak = tracemalloc.get_traced_memory()
                    tracemalloc.stop()
                    elapsed_time=end_time-start_time
                    exp_logger.debug(f' elapsed time (s): {elapsed_time}')
                except TimeoutException as e:
                    exp_logger.warning(f"Timed out! {alg.__name__} {R_name} n={len(A)} h={len(H)}")
                    mem_current, mem_peak = tracemalloc.get_traced_memory()
                    tracemalloc.stop()                                
                    elapsed_time = "timeout"
                    FCSS = CSS_timeout                    
                n_edges = [len(pi[0].edges()) for pi in Pi]
                n_pivotals = [len(pi[1]) for pi in Pi]
                results.loc[len(results)] = [len(A), alg.__name__, len(H), cf, R_name, FCSS['v'], elapsed_time, mem_peak, n_edges, n_pivotals]
            results.to_csv(file_name,  mode='a', header=False, index=False)