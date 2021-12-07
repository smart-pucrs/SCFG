import os, sys; sys.path.append(os.path.dirname(os.path.realpath(__file__)))
import logging
import time

from distribution import *
from gen_seqvs_input import gen_single_instance
from importlib import reload
reload(logging)

PATH_FILE = os.path.dirname(os.path.realpath(__file__))
logging.basicConfig(filename=PATH_FILE+'/h_debug.log', filemode='w', level=logging.DEBUG)
exp_logger = logging.getLogger()

if __name__ == "__main__":
    exp_logger.info("Generating instances for SEQVS experiments")
    exp_logger.info(f"   {time.asctime(time.localtime(time.time()))}")

    max_ag = 4   
    cfs = [ndcs]
    range_A = range(2, max_ag+1)

    for root, dirs, files in os.walk(f"{PATH_FILE}/instances"):
        for file in files:
            os.remove(os.path.join(root, file))

    exp_number = 0
    for cf in cfs:
        exp_logger.info(f'Characteristic Function {cf.__name__}')
        for n in range_A:
            for h in range(2, max_ag+1, 1):
                reset()
                exp_number += 1
                gen_single_instance(n, h, cf, rate_pi=3, p_edges=.6, id=exp_number)
               