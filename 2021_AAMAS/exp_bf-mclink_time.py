import os, sys; sys.path.append(os.path.dirname(os.path.realpath(__file__)))
import logging
import math
import signal
import time
import pandas as pd 

from alg_bruteforce import bruteforce
from alg_mclink import mclink, V_R_S
from gen_input import gen_A, gen_H

from importlib import reload
reload(logging)
PATH_FILE = os.path.dirname(os.path.realpath(__file__))

logging.basicConfig(filename=PATH_FILE+'/h_debug.log', filemode='w', level=logging.DEBUG)
exp_logger = logging.getLogger()

class TimeoutException(Exception): pass
def signal_handler(signum, frame):
    raise TimeoutException("Timed out!")

if __name__ == "__main__":
    exp_logger.info("Evaluating different Algorithms in the same Problem")
    exp_logger.info(f"   {time.asctime(time.localtime(time.time()))}")

    columns = ['n', 'alg', 'h', 'cf', 'time', 'value']
    df = pd.DataFrame([], columns = columns) 
    file_name = f'{PATH_FILE}/exp_bf-mclink_time.csv'
    df.to_csv(file_name, index=False)
    del df

    algorithms = [bruteforce, mclink]
    cf = lambda c: math.pow(len(c), 2)
    range_A = [8,9,29,49,69]
    max_bf = 9
    max_h = 9
    FCSS_timeout = {'v':math.inf, 'h':[(0, {})]}
    TIMEOUT = 60*60 # in seconds 

    for n in range_A:
        A = gen_A(n)            
        exp_logger.info(f'Sequence for A = {A}')  
        for h in range(1, max_h+1, 1):
            if h > n: continue
            H = [cf] * h
            exp_logger.info(f'{h} levels')
            results = pd.DataFrame([], columns = columns) 
            for alg in algorithms:
                if alg.__name__ == 'bruteforce' and n > max_bf: continue

                exp_logger.info(f'Running {alg.__name__} cf={cf.__name__} n={n} h={h}')
                exp_logger.info(f"  {time.asctime(time.localtime(time.time()))}")
                signal.signal(signal.SIGALRM, signal_handler)
                signal.alarm(TIMEOUT) 
                try:
                    start_time = time.time()
                    FCSS_star = alg(A, H, V_R_S)                            
                    end_time = time.time()
                    signal.alarm(0)
                    elapsed_time=end_time-start_time
                    exp_logger.debug(f' elapsed time (s): {elapsed_time}')
                except TimeoutException as e:
                    exp_logger.warning(f"Timed out! {alg.__name__} cf={cf.__name__} n={n} h={h}")#
                    elapsed_time = "timeout"
                    FCSS_star = FCSS_timeout                    
                results.loc[len(results)] = [len(A), alg.__name__, h, cf.__name__, elapsed_time, FCSS_star["v"]]
            results.to_csv(file_name,  mode='a', header=False, index=False)