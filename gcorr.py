import networkx as nx
from backstuff import *

def isCreator(G, cr, attr):
    if G.nodes[cr][attr] == G.nodes[cr]['pid']:
        return True
    return False


def check_out_edge(G, v, name="follow"):
    res = None
    for (x, y, z) in list(G.out_edges(v, keys=True)):
        if (z==name and G.nodes[v]['pid']==G.nodes[y]['pid']):
            if G.nodes[y].get('isIHolder', None):
                return y
            res = True
    return res


def process_si_syscall(G, v, sys_name = "setpgid", cnt=Counter(6000)): # generalize this to resolve_dependency instead direct c==v_creator setting (base algorithm)
    for (x, y, z) in list(G.in_edges(v, keys=True)):
        if (z.startswith("setpgid")): # get c==v_creator
            if not G.nodes[x].get('isIHolder', None): # if it is not holder
                outg_node = check_out_edge(G, x, name="follow")
                if outg_node == True: #if it is intermediate state
                    # создадим дополнительный носитель
                    interm = get_free_cnt(cnt)
                    G.add_node(interm)
                    G.nodes[interm].update({'pid': interm,
                                            'sid': G.nodes[x]['sid'],
                                            'ppid': G.nodes[x]['pid'],
                                            'pgid': G.nodes[x]['pgid'],

                                            'addedin': 'gcorr',
                                            'handled':True,
                                            'isIHolder': True})
                elif isinstance(outg_node, int):
                    interm = outg_node
                else:
                    return False
                # совершим перевешивание:
                G.remove_edge(x,v)
                G.add_edge(x, interm, 'fork()')
                G.add_edge(interm, v, z)

    return True


def post_corr(G, ctx, cnt=Counter(6000), K=['pgid','pid']):
    if 'pgid' in K:
        call_name = "setpgid"
    else:
        print("Not implemented yet")
        return -1

    for v in list(nx.dfs_preorder_nodes(G)): # add closure for redundant nodes elimination (TODO)
        pp = process_si_syscall(G, v, sys_name=call_name, cnt=cnt)
        if pp:
            print("Added intermediate holder of pgid value for node", v, G.nodes[v], pp)
    return G


