import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import itertools

def bf_mclink_value(df, h, y, y_label):
    fig, axs = plt.subplots(2, 5)
    axs = axs.reshape(-1)

    cfs = df['cf'].unique()
    all_ag = results.loc[results['n'] >= h, 'n'].unique() 
    set_1 = results.loc[(results['n'] >= h) & (results['h'] == h)]   

    colours = itertools.cycle(('purple','blue'))
    linestyle = itertools.cycle(('*', 'v')) 
    for i, cf in enumerate(cfs):
        set_2 = set_1.loc[set_1['cf'] == cf]    
        for j, approach in enumerate(set_2['alg'].unique()):
            data = set_2.loc[(set_2['alg'] == approach) & (set_2['time'] != 'timeout')]     
            data['time'] = data['time'].astype(float)       
            axs[i].plot(data['n'], data[y], marker=next(linestyle), color=next(colours), label=approach)
        axs[i].legend()   
        axs[i].set_title(cf) 
        if y == 'time':
            axs[i].set_yscale('log')
        if i in [0, 5]:
            axs[i].set_ylabel(y_label,labelpad=0)
        if i in range(5,10):
            axs[i].set_xlabel('|A|')
        axs[i].set_xticks(all_ag)
    fig.set_size_inches(15, 6)
    return fig

def mclink_time(df, hs=[]):
    linestyle = itertools.cycle(('+', '.','*')) 
    fig, ax = plt.subplots()

    all_ag = df['n'].unique()
    if len(hs) == 0:
        hs = df['h'].unique()
    for h in hs: 
        data = df.loc[(df['h'] == h) & (df['n'] >= h)]
        ax.plot(data['n'], data['time'], marker=next(linestyle), label=df['alg'].unique()[0]+f"_h={h}")
    ax.legend()   
    ax.set_yscale('log')
    ax.set_ylabel('Time in seconds (log scale).',labelpad=0)
    ax.set_xlabel('|A|')
    ax.set_xticks(range(min(hs),max(df['n'].unique())+1,5))
    fig.set_size_inches(12, 6)
    return fig

def bf_mclink_time(df, ags_mc, ags_bf):
    fig, ax = plt.subplots()

    all_ag = df['n'].unique()
    hs = df['h'].unique()
    df = df.loc[df['n'] <= max(all_ag)]

    colours = ['purple','blue','orange','green','red','black']
    linecolour = itertools.cycle([c for c in colours for i in range(2)]) 
    linestyle = itertools.cycle(('v')) 
    for ag_mc in ags_mc: 
        data = df.loc[(df['n'] == ag_mc)]
        data['time'] = data['time'].astype(float) 
        ax.plot(data['h'], data['time'], marker=next(linestyle), label=data['alg'].unique()[0]+f"_|A|={ag_mc}")   
    linestyle = itertools.cycle(('*','v')) 
    for ag_bf in ags_bf: 
        pre_data = df.loc[(df['n'] == ag_bf) & (df['h'] <= ag_bf)]
        pre_data['time'] = df['time'].replace(['timeout'],[np.nan])
        pre_data['time'] = pre_data['time'].astype(float) 
        for alg in pre_data['alg'].unique(): 
            data = pre_data.loc[pre_data['alg']==alg]
            ax.plot(data['h'], data['time'], marker=next(linestyle), color=next(linecolour), label=alg+f"_|A|={ag_bf}")          
    ax.legend()   
    ax.set_yscale('log')
    ax.set_ylabel('Time in seconds (log scale).',labelpad=0)
    ax.set_xlabel('h')
    ax.set_xticks(hs)
    fig.set_size_inches(12, 6)
    return fig

if __name__ == "__main__":
    PATH_FILE = os.path.dirname(os.path.realpath(__file__))

    # results = pd.read_csv(PATH_FILE+'/exp_bf-mclink_time.csv') 
    # results['alg'] = results['alg'].replace(['mclink'],['MC-Link'])
    # results['alg'] = results['alg'].replace(['bruteforce'],['Brute-Force'])
    # bf_mclink_time(results, [29,49,69], [8,9])

    # results = pd.read_csv(PATH_FILE+'/exp_mclink_time.csv')
    # mclink_time(results, hs=list(range(10,101,10)))

    results = pd.read_csv(PATH_FILE+'/exp_bf-mclink_value.csv') 
    results['alg'] = results['alg'].replace(['mclink'],['MC-Link'])
    results['alg'] = results['alg'].replace(['bruteforce'],['Brute-Force'])
    results['cf'] = results['cf'].str.replace('_',' ')
    chart = bf_mclink_value(results, 3, 'value', 'Value for an FCSS.')
    
    plt.savefig(PATH_FILE+"/chart.pdf",bbox_inches='tight')