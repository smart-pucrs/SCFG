import os
import matplotlib.pyplot as plt
import pandas as pd

if __name__ == "__main__":
    import itertools
    path_dir = os.path.dirname(os.path.realpath(__file__))
    path_dir_chart = path_dir+"/charts"
    path_dir_results = path_dir+"/results"
 
    approach_names = ['fixed_3_140','hybrid_3_100','fixed_3_100','hybrid_3_140']
    approach_legends = ['fixed_141','hybrid_101','fixed_101','hybrid_141']

    colors = itertools.cycle(['green','blue','purple','orange'])
    markers = itertools.cycle(('p', '*', 'o', 5))  
    
    plt.rcParams['figure.dpi'] = 50
    
    plt.figure(dpi=10).set_size_inches(8, 3)
    ax = plt.axes()    

    df = pd.read_csv(f'{path_dir_results}/comparing_instances.csv')
    
    approaches = df.groupby('approach')

    df_found = pd.read_csv(f'{path_dir_results}/comparing_founds.csv')
    approaches_found = df_found.groupby('approach')
    for name in approach_names:
        approach = approaches_found.get_group(name)
        data = df.loc[(df['approach']==name)]
        ax.plot(approach['time'], approach['id'], linestyle="None", marker='.', ms=.05, color=next(colors), label=None)
        print(f"done for {name} {len(approach['id'])}")

    for name, legend in zip(approach_names, approach_legends):
        approach = approaches.get_group(name)
        ax.plot(approach['time'], approach['value'], linestyle='None', marker=next(markers), color=next(colors), label=legend)

    minutes = 60
    counter = [r for r in range(0,(60*60)+1,60*5)]
    ax.set_xticks([r for r in range(0,(60*minutes)+60,60*5)])
    ax.set_xlabel('Time in seconds.')
    ax.set_ylabel('Quality of the solution.')

    handles,labels = ax.get_legend_handles_labels()
    handles = [handles[2], handles[1], handles[0], handles[3]]
    labels = [labels[2], labels[1], labels[0], labels[3]]
    ax.legend(handles,labels)

    plt.savefig(f"{path_dir_chart}/quality_instances.pdf",bbox_inches='tight')