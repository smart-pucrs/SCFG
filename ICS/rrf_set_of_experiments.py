import os, sys
import time;  sys.path.append(os.path.dirname(os.path.realpath(__file__)))
import logging
import pandas as pd

def run_instance(result_df, found_df, folder, n, roles_per_personnel, hybrid, timeout):    
    path_dir_instances = os.path.dirname(os.path.realpath(__file__))+"/instances"
    path_dir_results = os.path.dirname(os.path.realpath(__file__))+"/results/"+folder

    import RRF as rrf
    import cf
    from uctseq_seqsvs import MCTS   
    import relation as Rel

    logging.info("Roaring River Flood Problem")
    logging.info(f"n={n} roles={roles_per_personnel} hybrid={hybrid}")

    instance = rrf.RRF.load_instance(path_dir_instances, f"RRF_A={n}_adopt={roles_per_personnel}_H=3", f"RRF_relationship_A={n}")

    if hybrid:
        instance.make_it_hybrid(goals="/data/rrf_goals.yml")

    # swap 1 and 3
    struc1 = instance._structures[0]
    instance._structures[0] = instance._structures[2]
    instance._structures[2] = struc1
    instance.add_chief()

    instance.set_cf(0, lambda C: cf.v_1(C, 0, hybrid=hybrid))
    instance.set_cf(1, lambda C: cf.v_1(C, 1, hybrid=hybrid))
    instance.set_cf(2, lambda C: cf.v_1(C, 2, hybrid=hybrid))
    instance.set_cf(3, lambda C: 0)
    cf.upsidedown = True
    cf.rrf = instance
    rrf.instance = instance

    Rel.initiliase(instance)
    R = Rel.sub_inv_R_ICS if hybrid==False else Rel.sub_inv_R_ICS_hybrid

    time.sleep(1)
    start_time = time.time()
    FCSS, intermediary, found = MCTS(instance.A, instance.H, instance.Pi, R, start_time, degree=5, depth=3, gamma=0.7, end_time=timeout, folder_result=path_dir_results)
    logging.info(f' elapsed time (s): {time.time()-start_time}')

    results = pd.DataFrame([], columns = columns)   
    for v, t in intermediary:
        results.loc[len(results)] = [folder, v, t]
    results.to_csv(result_df,  mode='a', header=False, index=False)

    results_found = pd.DataFrame([], columns = columns_found)   
    for id, t in found:
        results_found.loc[len(results_found)] = [folder, id, t]
    results_found.to_csv(found_df,  mode='a', header=False, index=False)

def clean_results():
    import shutil
    PATH_FILE = os.path.dirname(os.path.realpath(__file__))+"/results"

    if not os.path.exists(PATH_FILE):
        os.makedirs(PATH_FILE)
    for root, dirs, files in os.walk(PATH_FILE):
        for file in files:
            os.remove(os.path.join(root, file))
        for dir in dirs:
            shutil.rmtree(os.path.join(root, dir))
            
    PATH_FILE = os.path.dirname(os.path.realpath(__file__))+"/charts"

    for root, _, files in os.walk(PATH_FILE):
        for file in files:
            os.remove(os.path.join(root, file))

columns = ['approach','value', 'time']
columns_found = ['approach','id', 'time']

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)  
    logging.info("Experiments for the RRF problem")

    # INSTANCES
    instances = []
    instances.append((100, 3, False, 60*30))
    instances.append((140, 3, False, 60*30))
    instances.append((100, 3, True, 60*60))
    instances.append((140, 3, True, 60*60))

    clean_results()

    df = pd.DataFrame([], columns = columns) 
    result_df = f'{os.path.dirname(os.path.realpath(__file__))}/results/comparing_instances.csv'
    df.to_csv(result_df, index=False)
    del df

    df = pd.DataFrame([], columns = columns_found) 
    found_df = f'{os.path.dirname(os.path.realpath(__file__))}/results/comparing_founds.csv'
    df.to_csv(found_df, index=False)
    del df
    
    for instance in instances:
        folder = 'hybrid' if instance[2] else 'fixed'
        run_instance(result_df, found_df, f"{folder}_{instance[1]}_{instance[0]}", n=instance[0], roles_per_personnel=instance[1], hybrid=instance[2], timeout=instance[3])

    logging.info("All experiments are done!")
