import logging
import itertools
import time
import RRF as rrf
import relation as Rel

def clean_up_FCSS_dir():
    PATH_FILE = os.path.dirname(os.path.realpath(__file__))+"/FCSSs"

    if not os.path.exists(PATH_FILE):
        os.makedirs(PATH_FILE)

    for root, _, files in os.walk(PATH_FILE):
        for file in files:
            os.remove(os.path.join(root, file))

if __name__ == "__main__":
    import os, sys; sys.path.append(os.path.dirname(os.path.realpath(__file__)))
    import tracemalloc

    from uctseq_seqsvs import MCTS   
    import cf

    folder = os.path.dirname(os.path.realpath(__file__))+"/instances"

    logging.basicConfig(level=logging.INFO)

    logging.info("Roaring River Flood")

    # INSTANCES
    n, hybrid, timeout = 100, False, 30
    # n, hybrid, timeout = 140, False, 30
    # n, hybrid, timeout = 100, True, 60
    # n, hybrid, timeout = 140, True, 60
    roles_per_personnel = 3 # we always assume a personnel can adopt at most 3 roles 

    instance = rrf.RRF.load_instance(folder, f"RRF_A={n}_adopt={roles_per_personnel}_H=3", f"RRF_relationship_A={n}")

    if hybrid:
        instance.make_it_hybrid(goals="/data/rrf_goals.yml")

    # in our computation we start off from the strike-team/task-force/single-resource hierarchical level
    # swap 1 and 3
    struc1 = instance._structures[0] 
    instance._structures[0] = instance._structures[2]
    instance._structures[2] = struc1    
    instance.add_chief()

    instance.set_cf(0, lambda C: cf.v_1(C, 0, hybrid=hybrid))
    instance.set_cf(1, lambda C: cf.v_1(C, 1, hybrid=hybrid))
    instance.set_cf(2, lambda C: cf.v_1(C, 2, hybrid=hybrid))
    instance.set_cf(3, lambda C: 0)
    cf.rrf = instance
    cf.upsidedown = True

    A = list(instance.A)
    until = [len(A), len(A), instance.span_of_control+1]
    instance.next_leaders = []
    for i, s in enumerate(instance.Pi, start=1):
        instance.next_leaders.append(set(itertools.chain(*[s[0] for s in instance.Pi[i:]])))

    rrf.instance = instance

    clean_up_FCSS_dir()

    logging.info(f" for: |A|={len(instance.A)}, |H|={len(instance.H)}")
    Rel.initiliase(instance)

    folder_result = os.path.dirname(os.path.realpath(__file__))+"/FCSSs/"
    tracemalloc.start()
    start_time = time.time()

    R = Rel.sub_inv_R_ICS if hybrid==False else Rel.sub_inv_R_ICS_hybrid
    FCSS, _, found = MCTS(instance.A, instance.H, instance.Pi, R, start_time, degree=5, depth=3, gamma=0.7, end_time=timeout, folder_result=folder_result)

    logging.info(f' elapsed time (s): {time.time()-start_time}')
    current, peak = tracemalloc.get_traced_memory()
    print(f"Current memory usage is {current / 10**6}MB; Peak was {peak / 10**6}MB")

    tracemalloc.stop()
    logging.debug(f"found {len(found)} FCSSs")
