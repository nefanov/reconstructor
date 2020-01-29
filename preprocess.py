import networkx as nx
from networkx.algorithms.dag import topological_sort
from networkx.algorithms.traversal.depth_first_search import dfs_tree
from cl import Counter
from closures import save_and_draw_graph

def acquire_syscall(G, src, dst):
    # получение помеченного ребра системного вызова по атрибутам 2-х вершин
    # служит, чтобы не раздувать и без того громоздкие основные рутины поиска и переписывания
    if G.nodes[src]['pid'] == G.nodes[dst]['pid']:
        if G.nodes[dst]['pid'] == G.nodes[dst]['sid'] == G.nodes[dst]['pgid']:
            G.add_edge(src, dst, 'setsid()')
        elif G.nodes[dst]['pid'] == G.nodes[dst]['pgid'] and not G.nodes[dst]['pid'] == G.nodes[dst]['sid'] and G.nodes[src]['sid'] == G.nodes[dst]['sid']:
            G.add_edge(src, dst, 'setpgid(0, 0)')

    elif G.nodes[dst]['ppid'] == G.nodes[src]['pid'] and G.nodes[dst]['pgid'] == G.nodes[src]['pgid'] and G.nodes[dst]['sid'] == G.nodes[src]['sid']:
        G.add_edge(src, dst, 'fork()')
    elif G.nodes[dst]['pgid'] == G.nodes[src]['pgid'] and G.nodes[src]['sid'] == G.nodes[dst]['sid']:
        G.add_edge(src, dst, 'setpgid('+str(G.nodes[dst]['pid'])+", "+str(str(G.nodes[src]['pgid']))+')')
    return G


def get_pgroup_leader(G, val, cl, cnt=Counter(1000)):
    # после этого в графе будут все создатели пгрупп в нужных местах
    l = [x for x, y in G.nodes(data=True) if y['pid'] == y['pgid']==val]
    if l:
        return l[0]
    else:
        l = [x for x, y in G.nodes(data=True) if y['pid'] == val]
        if len(l):
            for upon_creator in l:
                if G.has_edge(l[0], upon_creator, key='pred'):                             #
                    G.remove_edge(l[0], upon_creator, 'pred')                              # intermediate_state
                    intermediate_node = cnt.inc()                                           #                ^ pred
                    G.add_node(intermediate_node)                                           # upon_creator  |
                    G.nodes[intermediate_node].update(G.nodes[upon_creator])
                    G.nodes[intermediate_node].update({'pid': val,
                                                       'pgid': val,
                                                       'ppid': G.nodes[l[0]]['ppid'],})

                    G.add_edge(intermediate_node, upon_creator, 'pred')
                    G.add_edge(upon_creator, intermediate_node, '_H')
                    G.add_edge(upon_creator, intermediate_node, 'setpgid(0,0)')
                    G.add_edge(l[0], intermediate_node, 'pred')
                    G.add_edge(intermediate_node, l[0], 'H')
                    return intermediate_node  # dependency is handled now
            # --------------------------------------------------------------------------------------------------------#
            # this is else: add pr

            intermediate_node = cnt.inc()
            creator = cnt.inc()
            G.add_node(intermediate_node)
            G.add_node(creator)
            G.nodes[intermediate_node].update(G.nodes[G.nodes[l[0]]['ppid']])
            G.nodes[intermediate_node].update(
                {'pid': G.nodes[l[0]]['pid'],
                 'pgid': G.nodes[G.nodes[l[0]]['ppid']]['pgid'],
                 'ppid': G.nodes[l[0]]['ppid'], })

            G.nodes[creator].update(G.nodes[G.nodes[l[0]]['ppid']])
            G.nodes[creator].update(
                {'pid': G.nodes[l[0]]['pid'],
                 'pgid': val,
                 'ppid': G.nodes[l[0]]['ppid'], })

            G.add_edge(intermediate_node, G.nodes[l[0]]['ppid'], 'pred')
            G.add_edge(G.nodes[l[0]]['ppid'], intermediate_node, '_ _H')
            G.add_edge(G.nodes[l[0]]['ppid'], intermediate_node, 'fork()')

            G.add_edge(creator, intermediate_node, 'pred')
            G.add_edge( intermediate_node, creator, 'setpgid(0, 0)')
            G.add_edge( intermediate_node, creator, '_ _ _H')
            G.add_edge(l[0], creator, 'pred')
            G.add_edge(creator, l[0], 'H')

            return intermediate_node  # dependency is handled now
        # -----------------------------------------------------------------------------------------------------------#
        else: # create absolutely new creator in the closure of sid
            intermediate_node = cnt.inc()
            G.add_node(intermediate_node)
            G.nodes[intermediate_node].update(G.nodes[cl])
            G.nodes[intermediate_node].update(
                {'pid': val, 'ppid': cl})

            G.add_edge(intermediate_node, cl, 'pred')
            G.add_edge(cl, intermediate_node, 'H')

            creator_node = cnt.inc()
            G.add_node(creator_node)
            G.nodes[creator_node].update(G.nodes[cl])
            G.nodes[creator_node].update(
                {'pid': val, 'pgid': val, 'ppid': cl, })
            G.add_edge(creator_node, intermediate_node, 'pred')
            G.add_edge(intermediate_node, creator_node, 'Hz')
            return creator_node


def preprocess_tree(T, attr_name, ctx, creators={}, cnt=Counter(100)): # test it before usage!
    # setting tree into consistent state (see reparent manual)
    init = [x for x in T.nodes() if T.in_degree(x) == 0 or x == 1][0]
    for p in list(T.nodes):
        try:
            if not T.nodes[p]['ppid'] in list(T.nodes):
                T.nodes[p]['ppid'] = init # init value
        except:
            print('catch', T.nodes[p],p)
            print('azaza')
    # now pstree is consistent
    subroots = list(T.successors(init))

    creators[1] = {init: init}
    for subroot in subroots:
        for item_ptr in dfs_tree(T, subroot):
            attr_val = T.nodes[item_ptr][attr_name]
            if attr_val == T.nodes[item_ptr]['pid']:            # creator criteria - replace if generalized
                creators[attr_val] = {item_ptr : subroot}        # check correctness also

    for subroot in subroots:
        for item_ptr in dfs_tree(T, subroot):
            attr_val = T.nodes[item_ptr][attr_name]

            if not attr_val == T.nodes[item_ptr]['pid']:        # handle holder - this node is not in current tree

                creator_location = creators.get(attr_val, None)
                if creator_location is None:
                    creator = attr_val#cnt.inc() - must be checket to unduplication
                    creators[attr_val] = {creator, creator}
                    T.add_node(creator)
                    T.nodes[creator].update(T.nodes[init])

                    T.nodes[creator].update({'ppid': init, 'pid': attr_val,})  # append entry
                    if T.nodes[item_ptr]['sid'] == attr_val:
                        T.nodes[creator].update({'pgid': attr_val,'sid': attr_val})
                    else:
                        T.nodes[creator].update({'pgid': attr_val,})
                    T.nodes[creator].update({'status': 0})
                    T.add_edge(init, creator, key='h-intermediate')


                    try:
                        T.remove_edge(T.nodes[subroot]['ppid'], subroot, key='h')
                    except:
                        pass
                    T.nodes[subroot].update({'ppid': attr_val})
                    T.add_edge(creator, subroot, 'h-rev_reparent')

                    # append node to root
                    pass

                elif attr_name in ['sid', 'pgid'] and attr_val == 1:
                    pass
                else:
                    try:
                        creator_subroot_val = creator_location[next(iter(creator_location))]
                    except TypeError:
                        creator_subroot_val = next(iter(creator_location))
                    if not creator_subroot_val == subroot:      # not from this subtree - condition (*) from scratch
                        creator = next(iter(creator_location))  # eject subtree which contains creator
                        intermediate_node = cnt.inc()
                        T.add_node(intermediate_node)
                        T.nodes[intermediate_node].update(T.nodes[creator])
                        T.nodes[intermediate_node].update({'pid': intermediate_node, 'ppid': creator})
                        T.nodes[intermediate_node].update({'status': 0})
                        try:
                            T.remove_edge(T.nodes[subroot]['ppid'], subroot, 'h')
                        except:
                            pass
                        T.nodes[subroot].update({'ppid': intermediate_node})  # connect current_subroot_val node to creator via intermediate state
                        T.add_edge(creator, intermediate_node,  'h-intermediate')
                        T.add_edge(intermediate_node, subroot, 'h-stitching_to_subtree')

                        break # dependency is handled now

                    else:  # everything is ok
                        continue

                if ctx.per_step_show:
                    save_and_draw_graph(T, num_palette=ctx.colors_dict, pic_name=ctx.compose_name("_preprocess"), show_graph=False)
                    ctx.op_inc()

    return T


def upbranch(G, src, tgt, attr_key, cnt):
    try:
        branch = list(nx.all_simple_paths(G, source=src, target=tgt))[0]
    except:
        return G
    if len(branch):
        branch = branch[::-1]
        node_ptr = branch[0]
    while node_ptr is not src:
        try:
            l=[x for x,y in G.nodes(data=True) if
           y['pid'] == G.nodes[node_ptr]['ppid']
           and y['sid'] == G.nodes[src]['sid']
           and y['pgid'] == G.nodes[src]['pgid']]
        except:
            print("fff")

        try:
            parent = l[0]
        except:
            try:
                parent = G.nodes[node_ptr]['ppid']
            except:
                return G
        if node_ptr == src:
            return G

        intermediate_state = node_ptr
        if not G.nodes[src]['sid'] == G.nodes[node_ptr]['sid'] or not \
                G.nodes[src]['pgid'] == G.nodes[node_ptr]['pgid']:
            intermediate_state = cnt.inc()
            G.add_node(intermediate_state)
            G.nodes[intermediate_state].update(G.nodes[src])
            G.nodes[intermediate_state].update({'pid': G.nodes[node_ptr]['pid'],
                                                'ppid': G.nodes[node_ptr]['ppid'],
                                                'isHandled': True})

        parent_intermediate_state = parent

        try:
            if not G.nodes[src]['sid'] == G.nodes[parent]['sid'] or not G.nodes[src]['pgid'] == G.nodes[parent]['pgid']:
                parent_intermediate_state = cnt.inc()
                G.add_node(parent_intermediate_state)
                G.nodes[parent_intermediate_state].update(G.nodes[src])
                G.nodes[parent_intermediate_state].update({'pid': parent,
                                                           'ppid': G.nodes[parent]['ppid'],
                                                           'isHandled': True})
        except:
            print("Err with", src, parent)

        if not parent_intermediate_state == parent:
            G.add_edge(parent_intermediate_state, parent, 'H')
            if G.nodes[parent]['pid'] == G.nodes[parent]['sid']:
                G.add_edge(parent_intermediate_state, parent, 'setsid()')
            G.add_edge(parent, parent_intermediate_state, 'pred')
            #maybe check to syscall setting
        if not intermediate_state == node_ptr:
            if G.nodes[node_ptr]['pid'] == G.nodes[node_ptr]['pgid']:
                G.add_edge(intermediate_state, node_ptr, 'setpgid(0, 0)')
            G.add_edge(intermediate_state, node_ptr, 'H')
            G.add_edge(node_ptr, intermediate_state, 'pred')

        G.add_edge(parent_intermediate_state, intermediate_state, 'fork()')
        G.add_edge(parent_intermediate_state, intermediate_state, 'H')

        node_ptr = parent_intermediate_state

    return G


def processing(G=nx.MultiDiGraph(), cnt=Counter(100), phase=1):

    init = [x for x in G.nodes() if G.in_degree(x) == 0 or x == 1][0]
    for item in dfs_tree(G, init):
        #processing_step(G=nx.MultiDiGraph(), cnt=Counter(100),item=item,init=init)
        if item == 1:
            G.nodes[item].update ({'isHandled': True})
            continue

        try:
            if G.nodes[item]['isHandled'] and phase <= 3:
                continue
        except Exception as e:
            pass

        parent = G.nodes[item]['ppid']

        if phase == 1 and G.nodes[parent]['sid'] == G.nodes[item]['sid'] and \
            G.nodes[parent]['pgid'] == G.nodes[item]['pgid'] \
                and G.nodes[item]['sid'] == G.nodes[item]['pgid']:
            G.add_edge(parent, item, "fork()")

        elif phase == 1 and (not G.nodes[item]['sid'] == G.nodes[item]['pid'] or
                             not G.nodes[item]['pgid'] == G.nodes[item]['pid']): # upbranch!
            G.nodes[item].update({'isHandled': True})
            #try:
            creatr_p = G.nodes[G.nodes[item]['sid']]['pid']
            if creatr_p == 0:
                creatr_p = 1
            upbranch(G, creatr_p, item, 'sid', cnt)

        elif phase == 2 and G.nodes[item]['pid'] == G.nodes[item]['sid'] == G.nodes[item]['pgid']:
            try:
                l = [x for x, y in G.nodes(data=True) if
                y['pid'] == G.nodes[item]['pid'] and not
                y['sid'] == G.nodes[item]['pid']] # there may be error - check it after 3-5 impl
                intermediate_state = l[0]
            except:
                intermediate_state = cnt.inc()
                G.add_node(intermediate_state)
                G.nodes[intermediate_state].update(G.nodes[G.nodes[item]['ppid']]) # maybe change to actual_parent?
                G.nodes[intermediate_state].update({'pid': G.nodes[item]['pid'],
                                                    'ppid': G.nodes[item]['ppid'],
                                                    'isHandled': False})
                G.add_edge(G.nodes[item]['ppid'], intermediate_state, '*H*')
                G.add_edge(G.nodes[item]['ppid'], intermediate_state, 'fork()')

                G.add_edge(intermediate_state, item, '*H*')
                G.add_edge(intermediate_state, item, 'setsid()')
                
        # pstree pgroup(set new pgroup) reconstruction
        elif phase == 3 \
                and G.nodes[item]['pgid'] == G.nodes[item]['pid'] \
                and not G.nodes[item]['sid'] == G.nodes[item]['pid']:

            l = [x for x, y in G.nodes(data=True) if
                 y['pid'] == G.nodes[item]['ppid'] and
                 y['sid'] == G.nodes[item]['sid']]  # not empty, elsewise wrong tree
            try:
                actual_parent = l[0]
            except:
                actual_parent = G.nodes[item]['ppid']

            #G.nodes[item].update({'isHandled':True})
            l = [x for x, y in G.nodes(data=True) if
             y['pid'] == G.nodes[item]['pid'] and
             y['sid'] == G.nodes[item]['sid']][0] # not empty, elsewise wrong tree
            try:
                intermediate_state = l[0]
            except:
                intermediate_state = cnt.inc()
                G.add_node(intermediate_state)

                G.nodes[intermediate_state].update(G.nodes[actual_parent])
                G.nodes[intermediate_state].update({'pid': G.nodes[item]['pid'], 'ppid': G.nodes[actual_parent]['pid']})

            G.add_edge(intermediate_state, actual_parent,"pred")
            G.add_edge(actual_parent, intermediate_state, "fork()")
            G.add_edge(actual_parent, intermediate_state, "H#")
            G.add_edge(item, intermediate_state, "pred")
            G.add_edge(intermediate_state, item, "setpgid(0, 0)")
            G.add_edge(intermediate_state, item, "H$")
            G.nodes[item].update({'isHandled': True})
        # intermediate pgroup(set new pgroup) reconstruction


        elif phase == 4 and \
                not G.nodes[item]['pid'] == G.nodes[item]['sid'] and \
                not G.nodes[item]['pid'] == G.nodes[item]['pgid']:
            get_pgroup_leader(G, G.nodes[item]['pgid'], G.nodes[item]['sid'], cnt)








        elif phase == 5 and not G.nodes[item]['pid'] == G.nodes[item]['sid']:

            if G.nodes[item]['pgid'] == G.nodes[item]['pid']:
                continue

            # find actual parent:
            l = [x for x, y in G.nodes(data=True) if
                 y['pid'] == G.nodes[item]['ppid'] and
                 y['sid'] == G.nodes[item]['sid']]
            try:
                if G.nodes[item]['pgid'] == G.nodes[item]['sid']:
                    parent = [i for i in l if G.nodes[i]['pgid'] == G.nodes[item]['sid']][-1]
                else:
                    parent = [i for i in l if G.nodes[i]['pgid'] == G.nodes[parent]['pgid']][-1] # Перезагружаем родителя - более актуальное состояние { not empty, else incorrect tree }
            except:
                try:
                    parent = l[-1]
                except:
                    parent = G.nodes[item]['ppid']

            if (not G.nodes[parent]['pgid'] == G.nodes[item]['pgid'] \
                    ) and \
                    G.nodes[parent]['sid'] == G.nodes[item]['sid']:
                flag = False
                try:
                    intermediate_state = [x for x, y in G.nodes(data=True) if
                     y['pid'] == G.nodes[item]['pid']
                        and y['sid'] == G.nodes[item]['sid']
                        and not y['pgid'] == G.nodes[item]['pgid']][-1] # THIS IS HEURISTICS - handle it as well.
                except:
                    flag = True
                    intermediate_state = cnt.inc()
                    G.add_node(intermediate_state) # создаётся
                    G.nodes[intermediate_state].update({'pid': G.nodes[item]['pid'],
                                                        'ppid': G.nodes[item]['pid'],
                                                        'sid': G.nodes[parent]['sid'],
                                                        'pgid': G.nodes[parent]['pgid'],
                                                        'isHandled': True})
                    print("Added intermediate state", G.nodes[intermediate_state])

                creator = [x for x, y in G.nodes(data=True) if y['pid'] == y['pgid'] == G.nodes[item]['pgid']][0]
                print("aaa")
                G.add_edge(intermediate_state, item, "follow")
                G.add_edge(item, creator, "creator_pgroup")
                G.add_edge(creator, item, "setpgid("+str(G.nodes[item]['pid'])+", "+str(G.nodes[item]['pgid'])+")")
                if flag:
                    G.add_edge(parent, intermediate_state, "HHH")
                    G.add_edge(parent, intermediate_state, "fork()")

    return G


def get_node_states(G, pid, attr_key, attr_val):
    res = [x for x, y in G.nodes(data=True) if
     y['pid'] == pid and y[attr_key] == attr_val]
    if len(res) > 0:
        return res[0]
    else:
        return None


def postprocess_graph(G=nx.MultiDiGraph(), cnt=Counter(100)):
    pass
    return G


def test1():
    import test_trees
    # test preprocessing

    G=preprocess_tree(test_trees.test1(), 'sid', creators={}, cnt=Counter(99))

    G = processing(G, cnt=Counter(100), phase=1)
    G = processing(G, cnt=Counter(200), phase=2)
    G = processing(G, cnt=Counter(300), phase=3)
    G = processing(G, cnt=Counter(400), phase=4)
    save_and_draw_graph(G)
    sys.exit(0)
    G = processing(G, cnt=Counter(500), phase=5)
    save_and_draw_graph(G)
    #G = process_tree()

    #postprocess_graph(G)

def test2():
    import test_trees
    G = preprocess_tree(test_trees.test2(), 'sid', creators={}, cnt=Counter(99))
    G = upbranch(G, 1, 5, 'sid', cnt=Counter(100))
    save_and_draw_graph(G)

def test3():
    import test_trees
    G = preprocess_tree(test_trees.test3(), 'sid', creators={}, cnt=Counter(99))
    ed = list(G.edges())
    G = processing(G, cnt=Counter(100), phase=1)
    G = processing(G, cnt=Counter(200), phase=2)
    G = processing(G, cnt=Counter(300), phase=3)
    G = processing(G, cnt=Counter(400), phase=4)
    G = processing(G, cnt=Counter(500), phase=5)
    save_and_draw_graph(G)
    pass

def test4():
    import test_trees
    G = preprocess_tree(test_trees.test4(), 'sid', creators={}, cnt=Counter(50))
    ed = list(G.edges())

    G = processing(G, cnt=Counter(100), phase=1)
    G = processing(G, cnt=Counter(200), phase=2)
    G = processing(G, cnt=Counter(300), phase=3)
    G = processing(G, cnt=Counter(400), phase=4)
    G = processing(G, cnt=Counter(500), phase=5)

    filter_edges = [(U,V,k) for U,V,k in G.edges(keys=True) if k=='h']
    G.remove_edges_from(filter_edges)
    filter_edges = [(U, V, k) for U, V, k in G.
        edges(keys=True) if k.startswith('pred') or k.startswith('parent') or k.startswith('creator_')
                    or k.startswith('Pre')]
    G.remove_edges_from(filter_edges)
    save_and_draw_graph(G)


def test5():
    import test_trees
    G = preprocess_tree(test_trees.test5(), 'sid', creators={}, cnt=Counter(50))
    ed = list(G.edges())
    #G.remove_edges_from(ed)
    G = processing(G, cnt=Counter(100), phase=1)
    G = processing(G, cnt=Counter(200), phase=2)
    G = processing(G, cnt=Counter(300), phase=3)
    G = processing(G, cnt=Counter(400), phase=4)
    G = processing(G, cnt=Counter(500), phase=5)
    filter_edges = [(U,V,k) for U,V,k in G.
        edges(keys=True) if k=='h']
    G.remove_edges_from(filter_edges)
    filter_edges = [(U, V, k) for U, V, k in G.
        edges(keys=True) if k.startswith('pred') or k.startswith('parent') or k.startswith('creator_')
                    or k.startswith('Pre') or k.startswith('H')]
    G.remove_edges_from(filter_edges)
    save_and_draw_graph(G)
import sys

def run_pipeline(T, sparse_edges=False, draw=False, save_list=None):
    cnt = Counter(1000)
    #check

    #save_and_draw_graph(T)
    #sys.exit(0)
    G=T
    #filter_edges = [(U, V, k) for U, V, k in G.
    #    edges(keys=True) if
    #                k.startswith('H') or k.startswith('*H*')]
    #G.remove_edges_from(filter_edges)
    #save_and_draw_graph(G)

    #sys.exit(0)

    G = preprocess_tree(T, 'sid', creators={}, cnt=cnt)
    G = processing(G, cnt=cnt, phase=1)
    G = processing(G, cnt=cnt, phase=2)
    save_and_draw_graph(G)
    sys.exit(0)
    G = processing(G, cnt=cnt, phase=3)
    G = processing(G, cnt=cnt, phase=4)
    G = processing(G, cnt=cnt, phase=5)

    if sparse_edges:
        filter_edges = [(U, V, k) for U, V, k in G.
            edges(keys=True) if k == 'h']
        G.remove_edges_from(filter_edges)
        filter_edges = [(U, V, k) for U, V, k in G.
            edges(keys=True) if k.startswith('pred') or k.startswith('parent') or k.startswith('*H*') or k.startswith('creator_')
                        or k.startswith('Pre') or k.startswith('H') or k.startswith('_H') or k.startswith('h-s') or k.startswith('h-i')  or k.startswith('h-r') or k.startswith('rev')]
        G.remove_edges_from(filter_edges)
    if draw:
        #G.add_node(4)
        #G.add_node(5)

        #G.nodes[4].update({'pid': 4, 'sid': 1, 'pgid': 2})
        #G.nodes[5].update({'pid':5,'sid':1,'pgid':3})
        #G.add_edge(1003, 5,'fork()')
        #G.add_edge(1004, 4, 'fork()')
        #G.add_edge(5, 2, 'setpgid(3,2)')
        #G.add_edge(4, 3, 'setpgid(2,3)')
        #G.remove_edge(1003,2)
        #G.remove_edge(1004, 3)
        save_and_draw_graph(G)
    if save_list:
        pass
    return G

import test_trees


if __name__ == '__main__':
    run_pipeline(test_trees.test4(), True, True)