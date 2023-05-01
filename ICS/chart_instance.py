import matplotlib.pyplot as plt
import numpy as np
import cf
import os

def autolabel(ax, rects):
   for rect in rects:
      height = rect.get_height()
      ax.annotate('{}'.format(height),
         xy=(rect.get_x() + rect.get_width() / 2, height),
         xytext=(0, 3), # 3 points vertical offset
         textcoords="offset points",
         ha='center', va='bottom')

def analyse_instance(instance, instance2):
    legend = {0: 'Sup.',1:'ACHO',2:'ADS',3:'ADT',4:'AETRT',5:'ASRT',6:'ASRTec',7:'VMT',8:'AADAT',9:'ABS'}
    width = 0.25
    margin = 0.05
    total = width+margin
    multi = 1.3

    counter_agents, counter_roles, counter_bound = rrf.compute_roles(instance)
    counter_agents2, _, _ = rrf.compute_roles(instance2)

    fig = plt.figure() 
    ax = fig.add_axes([0.1,0.1,0.8,0.8])

    req_roles = sorted(counter_agents.keys())
    positions = np.arange(len(req_roles))*multi
    position_x = positions - (total*1.3) 
    position_x[0] = -width/2
    bar_ag100 = ax.bar(position_x, [counter_agents.get(r, 0) for r in req_roles],  width-margin, color ='blue', label='number of agents able to adopt the role (out of 101)')
    position_x = positions - ((total+margin)/2.5)
    position_x[0] = width/2
    bar_ag140 = ax.bar(position_x, [counter_agents2.get(r, 0) for r in req_roles],  width-margin, color ='purple', label='number of agents able to adopt the role (out of 141)')

    position_x = positions + ((total+margin)/2.5)
    bar_leader = ax.bar(position_x[1:], [counter_roles.get(r, 0) for r in req_roles[1:]],  width-margin, color ='green', label='number of leaders requiring the role')
    position_x = positions + (total*1.3)
    bar_req = ax.bar(position_x[1:], [counter_bound.get(r, 0) for r in req_roles[1:]],  width-margin, color ='orange', label='maximum number of agents required for the role')

    ax.set_xticks(np.arange(len(req_roles)) * multi)
    ax.set_xticklabels([legend[r] for r in req_roles])

    ax.legend(loc='upper right')
    ax.set_ylabel("Number of Resources")

    autolabel(ax, bar_ag100)
    autolabel(ax, bar_ag140)
    autolabel(ax, bar_req)
    autolabel(ax, bar_leader)

    plt.xticks(rotation=45)
    fig.set_size_inches(12, 6)

if __name__ == "__main__":
    import RRF as rrf
    path_current_dir = os.path.dirname(os.path.realpath(__file__))

    upsidedown, per_role = False, 3

    instance_100 = rrf.RRF.load_instance(path_current_dir+'/instances', f"RRF_A=100_adopt={per_role}_H=3", "RRF_relationship_A=100")
    instance_100.add_chief(upsidedown=upsidedown)

    instance_140 = rrf.RRF.load_instance(path_current_dir+'/instances', f"RRF_A=140_adopt={per_role}_H=3", "RRF_relationship_A=140")
    instance_140.add_chief(upsidedown=upsidedown)
    
    # the problem is the same for both instances
    cf.rrf = instance_100
    rrf.instance = instance_100

    analyse_instance(instance_100, instance_140)

    plt.savefig(f"{path_current_dir}/charts/instance_{per_role}.pdf",bbox_inches='tight')
