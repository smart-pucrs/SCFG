from seqsvs_vs import check_SVS_no_graph
import itertools
import networkx as nx

def GenCS(base_CS, R, val, max_try, graph:nx.Graph, S:set, Z):   
    G_prime = prepare_graph_superset(base_CS, graph, S)

    for u, r in G_prime.edges():
        new_color = 'green'
        new_C = u.union(r)

        if len(new_C.intersection(S)) > 1:
            new_color = 'red'
        elif len(new_C) > max(Z):
            new_color = 'red'

        G_prime.add_edge(u, r, color=new_color, gain=cf_v(u.union(r), val)-cf_v(u,val)-cf_v(r,val))

    yield from search_G(base_CS, R, val, max_try, G_prime, S, Z, 0)

    CS_prime = set(G_prime.nodes())
    if check_SVS_no_graph(CS_prime, S, Z) and R(base_CS, CS_prime):      
        yield frozenset(CS_prime)

def cf_v(C, v):
    if isinstance(v, dict):
        return v[C]
    else:
        return v(C)

def prepare_graph_superset(CS, G, S):
    if len(CS) == 0: 
        return G
    
    new_G = G.copy()  
    for C in CS:
        edges_C = set()
        for a in C:
            if len(edges_C) == 0:
                edges_C = {t for _, t in G.edges(frozenset([a]))}
            else:
                edges_C = edges_C.intersection({t for _, t in G.edges(frozenset([a]))})

        if len(C)>1:
            for a in C:
                new_G.remove_node(frozenset([a]))

            for t in edges_C:
                C_prime = next(iter(filter(lambda C_temp: t.issubset(C_temp), CS)))

                if C == C_prime: 
                    continue

                new_G.add_edge(C, C_prime)
    return new_G

def search_G(base_CS, R, val, max_try, G, S, Z, counter):
    def contract(r, t, new_node, G):
        tempG = G.copy()
        tempG.add_node(new_node)

        for _, t_prime, color_prime in itertools.chain(G.edges(r,data='color'),G.edges(t,data='color')):            
            if color_prime == 'red':
                tempG.add_edge(new_node, t_prime, color='red')
            elif not tempG.has_edge(new_node, t_prime):
                new_color = 'green'
                new_C = new_node.union(t_prime)

                if len(new_C.intersection(S)) > 1:
                    new_color = 'red'
                elif len(new_C) > max(Z):
                    new_color = 'red'

                tempG.add_edge(new_node, t_prime, color=new_color, gain=cf_v(new_C, val)-cf_v(new_node,val)-cf_v(t_prime,val))     

        tempG.remove_node(r)
        tempG.remove_node(t)

        return tempG
    
    for u, r, _ in sorted([e for e in G.edges(data=True) if e[2]['color']=='green'], key=lambda x: x[2]['gain'], reverse=True):
        CS_prime = set(G.nodes()).union({u.union(r)}).difference({u}).difference({r})

        if not check_SVS_no_graph(CS_prime, S, Z) or not R(base_CS, CS_prime):      
            continue

        counter = 0   

        G_prime = contract(u, r, u.union(r), G)

        G.add_edge(u, r, color='red')   

        yield from search_G(base_CS, R, val, max_try, G_prime, S, Z, counter)

        yield frozenset(G_prime.nodes())

    for u, r, _ in sorted([e for e in G.edges(data=True) if e[2]['color']=='green'], key=lambda x: x[2]['gain'], reverse=True):
        counter+=1
        if counter > max_try:
            counter = 0
            yield None 

        G_prime = contract(u, r, u.union(r), G)
        G.add_edge(u, r, color='red')      

        yield from search_G(base_CS, R, val, max_try, G_prime, S, Z, counter)
        
    return