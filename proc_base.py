import networkx as nx
from predicats import *
from transformations import *
from backstuff import *
from preprocess import upbranch, preprocess_tree


def __upbranch(G, src, dst, cnt):
    branch = list(nx.all_simple_paths(G,source=src,target=dst))[0][::-1]
    node = dst
    while not node == src:
        parent = get_parent(G, node)
        interm = node
        interm_parent = parent
        print("parent before add node", G.nodes[node],':', G.nodes[parent])
        if not G.nodes[src]['sid'] == G.nodes[node]['sid'] or not G.nodes[src]['pgid'] == G.nodes[node]['pgid']:
            interm = get_free_cnt(cnt)
            G.add_node(interm)
            G.nodes[interm].update({'pid': G.nodes[node]['pid'],
                                    'sid': G.nodes[src]['sid'],
                                'ppid': G.nodes[node]['ppid'],
                                'pgid': G.nodes[node]['pgid'],
                                    'addedin': 'upbranch1'})#maybe check heuristics on pgid (node/src)

        if not G.nodes[src]['sid'] == G.nodes[parent]['sid'] or not G.nodes[src]['pgid'] == G.nodes[parent]['pgid']:
            interm_parent = get_free_cnt(cnt)
            G.add_node(interm_parent)
            G.nodes[interm_parent].update({'pid': G.nodes[parent]['pid'],
                                           'sid': G.nodes[src]['sid'],
                                            'ppid': G.nodes[parent]['ppid'],
                                            'pgid': G.nodes[src]['pgid'],
                                           'addedin': 'upbranch2'})
        if not interm_parent == parent:
            G.add_edge(parent,interm_parent, 'pred')
            if G.nodes[parent]['sid'] == G.nodes[parent]['sid']:
                G.add_edge(interm_parent, parent, 'setsid()')

        if not interm == node:
            G.add_edge(node, interm, 'pred')

        if interm_parent:
            node = interm_parent
            G.add_edge(interm_parent, interm, 'fork()')
            G.add_edge(interm_parent, interm, 'h')
        else:
            print("parsing error")
            return 1

    return G


def process1(T, A, K , L, CR, ctx):
    T.nodes[1].update({'handled': True})
    G=T
    cnt = Counter(1000)
    if len(CR) == 0:
        for _item in nx.dfs_preorder_nodes(G):
            if G.nodes[_item]['sid'] == G.nodes[_item]['pid']:
                CR.update({G.nodes[_item]['sid']: _item})
    for _item in list(nx.dfs_preorder_nodes(G)):
        item = G.nodes[_item]
        if G.nodes[_item].get('handled',False) == True:
            continue
        if a_1(item, G.nodes[item['ppid']]) and a_3(item, G.nodes[item['ppid']]) and a_10(item, item):
            G.add_edge(item['ppid'], _item, 'fork()')
            item['handled'] = True
            if ctx.per_step_show:
                print_fig(G, ctx, "_phase1")
        else:
            if not item['sid'] == item['pid'] or not item['pgid'] == item['pid']:
                creator = CR[item['sid']]
                upbranch(G, creator, _item, attr_key='sid', cnt=cnt)
                if ctx.per_step_show:
                    print_fig(G, ctx, "_phase1")
    return G


def process2(G, A, K, L, CR, ctx):
    flag = 1
    cnt = Counter(2000)
    for _item in list(nx.dfs_preorder_nodes(G)):
        item = G.nodes[_item]
        if G.nodes[_item].get('handled',False) == True:
            continue
        if a_2(item,item):
            for (x,y,z) in list(G.out_edges(_item, keys=True)):
                if (z=='pred' and not a_2(G.nodes[y], item)):
                    flag=0
                    break

            if flag==0:
                flag=1
                continue
            for (u,x,k) in list(G.in_edges(_item, keys=True)):
                #(k == 'pred' and a_0(G.nodes[x], item) and not a_1(G.nodes[x], item)) or
                if  ((k=='h')) and a_0(G.nodes[x], item) and not a_1(G.nodes[u], item)  and not a_10(G.nodes[u],G.nodes[u]):
                    TR1(G, _item, cnt) # intermediate state added
                    if ctx.per_step_show:
                        print_fig(G, ctx, "_phase2")
    return G

def process3(G,A,K,L,CR, ctx):
    cnt = Counter(3000)
    for _item in nx.dfs_preorder_nodes(G):
        item = G.nodes[_item]
        if G.nodes[_item].get('handled', False) == True:
            continue
        parent = get_parent(G, _item)
        if a_1(item, G.nodes[parent]) and a_3(item, G.nodes[parent]) and a_10(item, item):
            G.add_edge(parent, _item, 'fork()')
            item.update({'handled': True})
            if ctx.per_step_show:
                print_fig(G, ctx, "_phase3")
            continue
        if a_4(item,item):
            try:
                interm = [x for x, y in G.nodes(data=True) if
                          y['pid'] == item['pid'] and a_1(y, item)][0]
            except:
                TR2(G, _item, cnt)
                if ctx.per_step_show:
                    print_fig(G, ctx, "_phase3")
    return G

def process4(G, A, K, L, CR, ctx):
    cnt = Counter(4000)

    for _item in list(nx.dfs_preorder_nodes(G)):

        item = G.nodes[_item]
        if G.nodes[_item].get('handled',False) == True:
            continue
        PG = []
        pgleader = None
        parent = get_parent(G,_item)
        if not a_5(item,item):
            for node in nx.dfs_preorder_nodes(G, CR[item['sid']]):
                if a_4(G.nodes[node],item):
                    pgleader=node
                    break
                elif item['pgid'] == G.nodes[node]['pid']:
                    PG.append(node)
                    if ctx.per_step_show:
                        print_fig(G, ctx, "_phase4")

            if pgleader == None and len(PG) > 0:
                for i in PG[0:]:
                    for (u, x, k) in G.out_edges(i, keys=True):
                        if k == 'pred' and G.nodes[x]['pid'] == item['pgid']:
                            TR3(G, i, x, _item, cnt)
                            if ctx.per_step_show:
                                print_fig(G, ctx, "_phase4")
                            break
                continue

                TR4(G, PG, _item, cnt)
                if ctx.per_step_show:
                    print_fig(G, ctx, "_phase4")
            if pgleader == None and len(PG) == 0:
                TR5(G,cnt,_item,CR) # make whole independent creator
                if ctx.per_step_show:
                    print_fig(G, ctx, "_phase4")
    return G


def process5(G, A, K, L, CR, ctx):
    cnt = Counter(5000)
    a = list(nx.dfs_preorder_nodes(G))
    for _item in a:
        item = G.nodes[_item]
        if G.nodes[_item].get('handled', False) == True:
            continue
        if not a_5(item,item):
            try:
                interm = [x for x, y in G.nodes(data=True) if
                          y['pid'] == item['pgid']][0]
                need_extra_node = False
            except Exception as e:
                print(e)
                need_extra_node = True
            try:
                TR6(G, _item, interm)
            except Exception as e:
                print(e)
                pass

            _ = TR7(G, _item, need_extra_node, cnt)
            if ctx.per_step_show:
                print_fig(G, ctx, "_phase5")

            creator = [x for x, y in G.nodes(data=True) if y['pid'] == item['pgid'] and y['pgid'] == item['pgid']][0]
            #if need_extra_node:
            if not has_in_syscall(G,_item): # extensive behaviour: change it to more appropriate (TODO)
                TR8(G, _item, interm, creator)
                if ctx.per_step_show:
                    print_fig(G, ctx, "_phase5")
    return G
