import logging
import os
import matplotlib.pyplot as plt
import numpy as np

import RRF as rrf
import cf

def autolabel(ax, rects):
   for rect in rects:
      height = rect.get_height()
      ax.annotate('{}'.format(height),
         xy=(rect.get_x() + rect.get_width() / 2, height),
         xytext=(0, 3), # 3 points vertical offset
         textcoords="offset points",
         ha='center', va='bottom')

def quality_hierarchy(FCSS, hybrid, debug=True, new_dist=False):
    import matplotlib.patches as mpatches
    def is_upper_sup(C,level):
        return len(C)==1 and len(C.intersection(rrf.instance.L))>0 and not len(C.intersection(rrf.instance.Pi[level][1]))>0

    def get_hatch_relationship(C, level):
        if len(C.intersection(rrf.instance.Pi[level][1]))>0:
            return ''
        return r'\\\\'
    
    def get_hatch_disturbance(C, level):
        if len(C)==1:
            if len(C.intersection(rrf.instance.Pi[level][1]))>0:
                return r'\\\\'
        return ''
    
    goals = rrf.RRF.load_object("/data/rrf_goals.yml")
    
    fig, axs = plt.subplots(3, 1)
    width, margin = 0.5, 0.1

    C_withsup = mpatches.Patch(facecolor='green', edgecolor='white', hatch='',label='relationship')
    C_nosup = mpatches.Patch(facecolor='green', edgecolor='white', hatch=r'\\\\',label='relationship (no current level sup.)')
    dist = mpatches.Patch(facecolor='blue',label='disturbance')
    dist_superior = mpatches.Patch(facecolor='blue', edgecolor='white', hatch=r'\\\\',label='disturbance (current level sup.)')
    
    hierarchy = [[], [], [], []]
    for level in range(1,4):
        relationship = []
        roles = []
        ordered_CS = []
        hatches_relationship = []
        hatches_disturbance = []

        if level == 1:
            for C in sorted(FCSS[level], reverse=True, key=lambda e: len(e)):
                id = len(hierarchy[level])+1
                hierarchy[level].append((C, id, 0)) 
                ordered_CS.append(f'{id}\n({len(C)})')

                hatches_relationship.append(get_hatch_relationship(C, level))
                hatches_disturbance.append(get_hatch_disturbance(C, level))
                relationship.append(np.round(cf.relationship(C, level, hybrid),2))

                if is_upper_sup(C, level):
                    roles.append(0)
                else:
                    if new_dist:
                        roles.append(np.round(cf.disturbance_entropy(C, level, hybrid, debug),2))
                    else:
                        roles.append(np.round(cf.disturbance(C, level, hybrid, debug),2))
        else:
            for i, (C, id_C, _) in enumerate(hierarchy[level-1]):
                index = 1
                for C_prime in sorted(filter(lambda c: c.issubset(C), FCSS[level]),reverse=True, key=lambda e: (len(e),str(sorted(e)))):
                    id = f'{id_C}{index}'
                    index += 1
                    _, _, child_counter = hierarchy[level-1][i]
                    hierarchy[level-1][i] = (C, id_C, child_counter+1)
                    hierarchy[level].append((C_prime, id, 0))
                    ordered_CS.append(f'{id}\n({len(C_prime)})')

                    hatches_relationship.append(get_hatch_relationship(C_prime, level))
                    hatches_disturbance.append(get_hatch_disturbance(C_prime, level))
                    relationship.append(np.round(cf.relationship(C_prime, level, hybrid, debug),2))

                    if is_upper_sup(C_prime, level):
                        roles.append(0)
                    else:
                        if new_dist:
                            roles.append(np.round(cf.disturbance_entropy(C_prime, level, hybrid, debug),2))
                        else:
                            roles.append(np.round(cf.disturbance(C_prime, level, hybrid, debug),2))

        level -= 1
        positions = np.arange(len(ordered_CS))
        position_x = positions - width/2
        bar_relationship = axs[level].bar(position_x, list(map(lambda n: int(n*100), relationship)), width-margin, color='g', hatch=hatches_relationship, edgecolor='white', align='center',label='relationship')
        position_x = positions + width/2
        bar_roles = axs[level].bar(position_x, list(map(lambda n: int(n*100), roles)), width-margin, color='b', hatch=hatches_disturbance, edgecolor='white', align='center', label='disturbance')
        axs[level].set_xticks(range(len(ordered_CS)))
        axs[level].set_xticklabels(ordered_CS)
        axs[level].set_yticks([x for x in range(0,101,25)]+[115])
        axs[level].set_yticklabels([x for x in range(0,101,25)]+[None])

        level += 1
        average_relationship, samples = 0, 0
        for rel in relationship:
            if rel==0: continue
            average_relationship += rel
            samples += 1

        average_relationship = average_relationship/samples
        print(f"for level {level} average relationship is {average_relationship}")

        average_achieve, samples = 0, 0
        for (C, id, _) in hierarchy[level]:
            achieve = set()
            C_roles = set()
            for a in C:
                if a in rrf.instance.L: continue
                C_roles.update(rrf.instance._agents[a]['adopt'])
            for g, info in goals.items():
                if C_roles.issuperset(info['roles']):
                    achieve.add(g)
            if level==1:
                print(f"C{id} achieves {len(achieve)} IOs {achieve}")
            if len(C) > 1:
                samples += 1
                average_achieve += len(achieve)
        print(f"at level {level} average goals achieved {average_achieve/samples}")
        
        level -=1
        autolabel(axs[level], bar_relationship)
        autolabel(axs[level], bar_roles)
        print("ticks y axis ",  axs[level].get_yticks(), axs[level].get_yticklabels())

    axs[0].legend(handles = [C_withsup,C_nosup, dist, dist_superior], ncol=2)  
    axs[1].set_ylabel("Ratio in Percentage") 

    plt.subplots_adjust(left=0.1, bottom=0.1, right=0.9, top=0.9, wspace=0.3, hspace=0.25) 
    plt.margins(0.005, tight=True)
    
    axs[2].set_yticks([x for x in range(0,101,25)]+[115])
    axs[2].set_yticklabels([x for x in range(0,101,25)]+[None])

    fig.set_size_inches(25, 10)
    return fig

def read_FCSS(file_path, file_name):    
    import jsonpickle
    info = None
    with open(f"{file_path}/{file_name}", 'r+') as _file:
        info = jsonpickle.decode(_file.read())    
    return info

def read_last_FCSS(file_path):  
    os.chdir(file_path)

    file = sorted(os.listdir(), reverse=True)[0]

    FCSS = read_FCSS(file_path, file)

    return list(reversed(FCSS))

def do_chart(folder_chart, folder_results, n, per_role, hybrid, test=False, new_dist=False):
    logging.info(f"chart for n={n} roles={per_role} hybrid={hybrid}")
    plt.clf()
    path_current_dir = os.path.dirname(os.path.realpath(__file__))

    instance = rrf.RRF.load_instance(path_current_dir+'/instances', f"RRF_A={n}_adopt={per_role}_H=3", f"RRF_relationship_A={n}") 
    instance.add_chief(upsidedown=True)
    cf.upsidedown = False
    cf.rrf = instance
    rrf.instance = instance

    try: 
        if test:
            FCSS = read_last_FCSS(f"{path_current_dir}/FCSSs")
        else:
            FCSS = read_last_FCSS(f"{path_current_dir}/results/{folder_results}")   

        v_fcss = 0
        for l, CS in enumerate(FCSS):
            val = sum([cf.v_1(C, l, hybrid) for C in CS]) if l>0 else 0
            print(f"{l} {len(CS)} {sum([len(C) for C in CS])} {val}")
            v_fcss += val
        print(f"sequence value: {v_fcss}") 

        quality_hierarchy(FCSS, hybrid, debug=True, new_dist=new_dist)
        
        plt.savefig(f"{path_current_dir}/{folder_chart}/{folder_results}.pdf",bbox_inches='tight')
    except Exception as e:
        raise e

if __name__ == "__main__":
    n, per_role, hybrid, folder = 100, 3, False, 'fixed_3_100'
    # n, per_role, hybrid, folder = 140, 3, False, 'fixed_3_140'
    # n, per_role, hybrid, folder = 100, 3, True, 'hybrid_3_100'
    # n, per_role, hybrid, folder = 140, 3, True, 'hybrid_3_140'
    
    do_chart("charts", folder, n, per_role, hybrid, test=False, new_dist=True)