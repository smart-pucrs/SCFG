import logging
import itertools
import RRF as rrf

if __name__ == "__main__":
    import os, sys; sys.path.append(os.path.dirname(os.path.realpath(__file__)))

    folder = os.path.dirname(os.path.realpath(__file__))+"/instances"

    logging.basicConfig(level=logging.INFO)
    logging.info("Roaring River Flood")

    # we always consider:
    # * number of agents either 100 or 140 (plus the Operations Section Chief (implicitely added))
    # * a resource can adopt at most 3 roles
    # * span of control of 5
    # * a hierarchy of three levels (plus section level (implicitly added))

    n = 100
    # n = 140

    set_of_agents = rrf.RRF.generate_set_agents(n, span_of_control=5, max_number_of_roles=3, hierarchy_specification="/data/rrf_hierarchy.yml", goals="/data/rrf_goals.yml", roles="/data/rrf_roles.yml")
    constraints = rrf.RRF.generate_constraints(set_of_agents, h=3, span_of_control=5)

    instance = rrf.RRF(set_of_agents, constraints, span_of_control=5)

    instance.next_leaders = []
    for i, s in enumerate(instance.Pi, start=1):
        instance.next_leaders.append(set(itertools.chain(*[s[1] for s in instance.Pi[i:]])))
   
    rrf.instance = instance
    rrf.instance.save_instance(folder, max_number_of_roles_to_adopt=3)

    logging.info("new RRF instance successfully created")
