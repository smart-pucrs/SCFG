import os, sys; sys.path.append(os.path.dirname(os.path.realpath(__file__)))
import logging
import math
import time
import pandas as pd 
from alg_mclink import mclink, V_R_S
from gen_input import gen_A

from importlib import reload
reload(logging)
PATH_FILE = os.path.dirname(os.path.realpath(__file__))

logging.basicConfig(filename=PATH_FILE+'/debug.log', filemode='w', level=logging.DEBUG)
exp_logger = logging.getLogger()

if __name__ == "__main__":
    exp_logger.info("Evaluating MC-Link running time")
    exp_logger.info(f"   {time.asctime(time.localtime(time.time()))}")

    columns = ['n', 'alg', 'h', 'time', 'value']
    df = pd.DataFrame([], columns = columns) 
    file_name = f'{PATH_FILE}/exp_mclink_time.csv'
    df.to_csv(file_name, index=False)
    del df

    max_ag = 100
    cf = lambda c: math.pow(len(c), 2)
    range_A = range(1, max_ag+1)
    hs = range(10, max_ag+1, 10)
    
    for h in hs:
        H = [cf] * h  
        exp_logger.info(f'h={h} levels') 
        for n in range(h,max_ag+1):
            A = gen_A(n)             
            exp_logger.info(f'Sequence for n={n}')   
            results = pd.DataFrame([], columns = columns)             
            exp_logger.info(f"  {time.asctime(time.localtime(time.time()))}")
            start_time = time.time()   
            FCSS_star = mclink(A, H, V_R_S)                            
            end_time = time.time()
            elapsed_time=end_time-start_time
            exp_logger.debug(f' elapsed time (s): {elapsed_time}')                 
            results.loc[len(results)] = [len(A), 'MC-Link', h, elapsed_time, FCSS_star['v']]
            results.to_csv(file_name,  mode='a', header=False, index=False)
