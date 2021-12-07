import os, sys; sys.path.append(os.path.dirname(os.path.realpath(__file__)))
import logging
from seqvs_vs import check_VS, V, val

def bruteforce(A, H, Pi, G_R):
    FCSS_star = {'v':0, 'h':[(0, {})]}
    for CS in G_R(A, len(H), {}):
        VS = Pi[0]
        if check_VS(CS, VS[0], VS[1]):
            bruteforce_path(A, [(val(H[0], VS, CS), CS)], H, Pi, G_R, FCSS_star)
    return FCSS_star
def bruteforce_path(A, CSS, H, Pi, G_R, FCSS_star):
    if len(CSS) >= len(H):
        if V(H, Pi, [CS[1] for CS in CSS]) > FCSS_star['v']:
            FCSS_star['v'] = V(H, Pi, [cs[1] for cs in CSS])
            FCSS_star['h'] = CSS
        return     
    for CS in G_R(A, len(H), CSS[-1][1]):
        VS = Pi[len(CSS)]
        if check_VS(CS, VS[0], VS[1]):
            bruteforce_path(A, CSS+[(val(H[len(CSS)], VS, CS),CS)], H, Pi, G_R, FCSS_star)
    return

if __name__ == "__main__":
    import time
    import tracemalloc
    from gen_R import G_R_1, G_R_2, G_R_3, G_R_4
    from gen_seqvs_input import load_instance
    PATH_TO_FILE = os.path.dirname(os.path.realpath(__file__))+"/results/ssci_instances"
    logging.basicConfig(level=logging.DEBUG)
    logging.info("Bruteforce SEQVS Algorithm")

    A, H, Pi = load_instance(PATH_TO_FILE, "instance30_A=5_H=4_cf=ndcs.json")  
    logging.info(f" Instance: n={len(A)}, h={len(H)}")
    tracemalloc.start()
    start_time = time.time()
    FCSS_star = bruteforce(A, H, Pi, G_R_2)
    logging.info(f' elapsed time (s): {time.time()-start_time}')
    current, peak = tracemalloc.get_traced_memory()
    logging.info(f" current memory usage is {current / 10**6}MB; peak was {peak / 10**6}MB")
    tracemalloc.stop()

    logging.info(f'Total Value = {FCSS_star["v"]}')
    for v, CS in FCSS_star['h']:
        logging.info(f'V({CS}) = {v}')    