#this module named as "visualizer"
#from __future__ import print_function
import collections
import sys
import os
import copy
import psutil
import networkx as nx
import json
import random
from graphviz import Source
from networkx.drawing.nx_pydot import to_pydot
from networkx.algorithms.traversal.depth_first_search import dfs_tree
import matplotlib.pyplot as plt


def pick_rand_color(l=170, h=255,shift=50, step=10):
    r = lambda: random.randrange(l, h, step)
    (R,G,B) = (r(), r(), r())
    return ('#%02X%02X%02X' % (R,G,B),'#%02X%02X%02X' % (R-shift,G-shift,B-shift)) # pgroup color is lighter than session


def prepare_colors_dict(G, attributes=['pid', 'pgid', 'sid', 'ppid']):
    num_palette = dict()
    for i, node in enumerate(G.nodes):
        for tag in attributes:
            num_palette[G.nodes[node][tag]] = pick_rand_color()
    return num_palette

def prepare_colors_from_range(r=7000): # not accurate but universal method
    num_palette=dict()
    for idx in range(r):
        num_palette[idx] = pick_rand_color()

    return num_palette


def save_and_draw_graph(G, nm="____ddd____.dot", num_palette=dict(), extended=False, ppid=True, save_png=True, pic_name="pic.png", show_graph=True, visualize_by_colors=True):
    pdot = to_pydot(G)
    #num_palette = dict()
    #if visualize_by_colors:
        #num_palette = prepare_colors_dict(G)

    for i, node in enumerate(pdot.get_nodes()):
        if visualize_by_colors:
            try:
                clr_p, _ = num_palette[int(node.obj_dict['attributes'].get('pgid', 1))]
                _, clr_s = num_palette[int(node.obj_dict['attributes'].get('sid', 1))]
                clrp,_ = num_palette[int(node.obj_dict['attributes'].get('pid', 1))]
                clrg,_ = num_palette[int(node.obj_dict['attributes'].get('pgid', 1))]
                clrs,_ = num_palette[int(node.obj_dict['attributes'].get('sid', 1))]
                node.set_color('white')
                node.set_fillcolor(clrg+":"+ clrp+";0.25:"+clrs) #+";0.15:"+clrs)
                node.set_style('filled')
                #node.set_fontcolor(colors[random.randrange(len(colors))])
                #node.set_fillcolor(colors[random.randrange(len(colors))])
                #node.set_style(styles[random.randrange(len(styles))])
                #node.set_color(colors[random.randrange(len(colors))]
            except Exception as e:
                print(e)
                node.set_color('black')
            node.set_style('filled, rounded, wedged')
            #node.set_shape('square') #diamond, record


        else:
            node.set_style('rounded, filled')

        if extended:
            node.set_label(
            node.obj_dict['attributes'].get('pid', None) + ' ' +
                       node.obj_dict['attributes'].get('pgid', None) + ' ' +
                       node.obj_dict['attributes'].get('sid', None) + ' // ' + node.obj_dict['attributes'].get('ppid', None) + ' \n' +str(node)
        )
        else:
            node.set_label(
                node.obj_dict['attributes'].get('pid', None) + ' ' +
                node.obj_dict['attributes'].get('pgid', None) + ' ' +
                node.obj_dict['attributes'].get('sid', None) + ' ' + node.obj_dict['attributes'].get('ppid', None)
            )

    for i, edge in enumerate(pdot.get_edges()):
        ek = edge.obj_dict['attributes'].get('key', 'common')
        edge.set_label(ek)
        #edge.set_style('bold')
        if ek.startswith('fol'):
            edge.set_color('orange')
        if ek.endswith(')'):
            edge.set_color('black')
        elif ek == 'H':
            edge.set_color('red')
        elif ek == 'h':
            edge.set_color('lightgrey')
        else:
            edge.set_color('green') #"0.11 0.901 0.99")#'green')

    pdot.write_dot(nm)
    if save_png:
        pdot.write_png(pic_name)
        print("PNG-file saved to "+pic_name)
    s = Source.from_file(nm, )
    if show_graph:
        s.render(view=True)
        #s.attr(bgcolor='purple:pink', label='agraph', fontcolor='white')

    return G


class ps_tree:
    def __init__(self):
        pass

    def save(G, fname):
        json.dump(dict(nodes=[[n, G.node[n]] for n in G.nodes()],
                       edges=[[u, v, G.edge[u][v]] for u, v in G.edges()]),
                  open(fname, 'w'), indent=2)

    def load(fname):
        G = nx.MultiDiGraph()
        d = json.load(open(fname))
        G.add_nodes_from(d['nodes'])
        G.add_edges_from(d['edges'])
        return G

    def run_construct_tree(self, G, tree):
        self.construct_tree(min(tree), tree, G=G)

    def construct_tree(self, parent, tree, indent='', attrs=['pid', 'ppid','sid','pgid'], G=nx.MultiDiGraph()):
        content = {}
        try:
            name = psutil.Process(parent).name()
            for k in attrs:
                if k == 'pid':
                    content[k] = parent
                elif k == 'ppid':
                    content[k] = psutil.Process(parent).ppid()
                elif k == 'sid':
                    content[k] = os.getsid(parent)
                elif k == 'pgid':
                    content[k] = os.getsid(parent)
                elif k == 'uid':
                    content[k] = os.getuid(parent)

        except psutil.Error:
            name = "?"
        print(parent, name, [(key, val) for key, val in content.items()])
        G.add_node(parent)
        G.nodes[parent].update(content)
        G.add_edge(content['ppid'], parent, key='h')
        if parent not in tree:
            return
        children = tree[parent][:-1]
        for child in children:
            self.construct_tree(child, tree, indent + "| ", ['pid', 'ppid','sid','pgid'], G)
        child = tree[parent][-1]
        self.construct_tree(child, tree, indent + "  ", ['pid', 'ppid','sid','pgid'], G)

    '''pretty printer of trees'''
    def print_tree(self, parent, tree, indent='', attrs=['pid', 'ppid','sid','pgid']):
        content = {}
        try:
            name = psutil.Process(parent).name()

            for k in attrs:
                if k == 'pid':
                    content[k] = parent
                elif k=='ppid':
                    content[k] = psutil.Process(parent).ppid()
                elif k=='sid':
                    content[k] = os.getsid(parent)
                elif k=='pgid':
                    content[k] = os.getsid(parent)
                elif k=='uid':
                    content[k] = os.getuid(parent)

        except psutil.Error:
            name = "?"
        print(parent, name, [(key, val) for key,val in content.items() ])
        if parent not in tree:
            return
        children = tree[parent][:-1]
        for child in children:
            sys.stdout.write(indent + "|- ")
            self.print_tree(child, tree, indent + "| ")
        child = tree[parent][-1]
        sys.stdout.write(indent + "`_ ")
        self.print_tree(child, tree, indent + "  ")

    def get_tree(self):
        # construct a dict where 'values' are all the processes
        # having 'key' as their parent
        tree = collections.defaultdict(list)
        for p in psutil.process_iter():
            try:
                tree[p.ppid()].append(p.pid)
            except (psutil.NoSuchProcess, psutil.ZombieProcess):
                pass
        # on systems supporting PID 0, PID 0's parent is usually 0
        if 0 in tree and 0 in tree[0]:
            tree[0].remove(0)

        return tree

    def get_nx_tree(self):
        tree = self.get_tree()
        G = nx.MultiDiGraph()
        self.run_construct_tree(G, tree)
        return G

    def print(self):
        tree = self.get_tree()
        self.print_tree(min(tree), tree)


class reconstructor:
    class attr_type:
        def __init__(self, name='pgid', cl_attr='sid', level=2, atype='SI'):
            self.name = name
            self.cl_attr = cl_attr
            self.level = level
            self.type = atype

        def get_cl(self):
            return self.cl_attr

        def get_level(self):
            return self.level

    class Counter:
        def __init__(self, id):
            self.c = id

        def inc(self):
            self.c += 1
            return self.c

    '''add parent link, reverse pre-reparent and add creators(?)'''

    def compose_attr_hierarchy(self):
        return [self.attr_type('pgid', 'sid', 2, 'SI'), self.attr_type('sid', 'sid', 1, 'HI')]

    def search_attr_creator(self, G, attr, node, ts):
        trav_subtree = ts#dfs_tree(G, node)
        return [x for x, y in G.nodes(data=True) if
                                  y['pid'] == G.nodes[node][attr.name] and y[attr.cl_attr] == G.nodes[node][attr.cl_attr]
                                    and not x==node and not x in trav_subtree]

    def search_attr_cl_creator(self, G, attr, node,ts):
        trav_subtree = ts#dfs_tree(G, node)
        return [x for x, y in G.nodes(data=True) if
                                  y[attr.cl_attr] == G.nodes[node][attr.cl_attr] and y['pid'] == G.nodes[node][attr.cl_attr]
                                    and not x==node and not x in trav_subtree]

    def search_attr_holder_cl_creator(self, G, attr, node,ts):
        trav_subtree = ts#dfs_tree(G, node)
        return [x for x, y in G.nodes(data=True) if
                                  y[attr.cl_attr] == G.nodes[node][attr.cl_attr]
                                    and not x==node and not x in trav_subtree]


    def preprocess(self):
        cnt = self.cnt
        G = self.RGraph
        root = [x for x in G.nodes() if G.in_degree(x) == 0 or x == 1][0]
        for node in nx.algorithms.dfs_preorder_nodes(G, root):
            if G.nodes[node]['ppid'] == 1:
                attr = self.compose_attr_hierarchy()[0]
                # в случае обобщения нужно будет выбрать все атрибуты и замыкания, и разыграть между ними порядок
                ts = dfs_tree(G, node)
                cand = self.search_attr_creator(G, attr, node,ts)
                cand_cl = self.search_attr_cl_creator(G, attr, node,ts)
                cand_holder_cl = self.search_attr_holder_cl_creator(G, attr, node,ts)
                if len(cand) > 0:
                    candidate_node = cand[0]
                    #G.add_edge(node, candidate_node, 'parent')
                    G.nodes[node]['ppid'] = candidate_node
                    continue
                elif len(cand_cl) > 0:
                    candidate_node = cand_cl[0]
                    #G.add_edge(node, candidate_node, 'parent')
                    G.nodes[node]['ppid'] = candidate_node
                    continue
                elif len(cand_holder_cl) > 0:
                    # it seems probably strange! maybe incorrect process tree!!! Check it!
                    # разве что это "early-clustering"
                    candidate_node = cand_cl[0]
                    #G.add_edge(node, candidate_node, 'parent')
                    G.nodes[node]['ppid'] = G.nodes[candidate_node]['ppid']
                    # add 3 .. --> 3 3 3
                    node_new = cnt.inc()
                    G.add_node(node_new)
                    G.nodes[node_new].update({'pid':G.nodes[node][attr.cl_attr],
                                              'ppid':G.nodes[candidate_node]['ppid'],
                                              'sid':G.nodes[G.nodes[candidate_node]['ppid']]['sid'],
                                              'pgid':G.nodes[G.nodes[candidate_node]['ppid']]['pgid']})
                    for _,b,c in G.edges([candidate_node], keys=True):
                        if c=="parent":
                            G.add_edge(node_new,b)
                            G.nodes[node_new].update(
                                {'pid': G.nodes[node][attr.cl_attr],
                                  'ppid': G.nodes[b]['pid'],
                                  'sid': G.nodes[b]['sid'],
                                  'pgid': G.nodes[b]['pgid']})
                            continue


                    node_new_2 = cnt.inc()
                    G.add_node(node_new_2)
                    G.nodes[node_new_2].update(
                        {'pid': G.nodes[node][attr.cl_attr],
                         'ppid': G.nodes[node_new]['pid'],
                         'sid': G.nodes[node][attr.cl_attr],
                         'pgid': G.nodes[node][attr.cl_attr]})
                    G.add_edge(node_new_2, node_new, "pred")
                    #G.add_edge(node_new_2,G.nodes[b]['pid'],"parent")
                    #G.add_edge(candidate_node, node_new_2, "parent")
                    #G.add_edge(node, node_new_2, "parent")
                    G.nodes[node].update({'ppid':G.nodes[node][attr.cl_attr]})

                    continue
            #if G.has_edge(G.nodes[node]['ppid'], node):
            #    G.add_edge(node, G.nodes[node]['ppid'], 'parent')
        return


    def convert_tree_from_pstree(self,tree):
        p = ps_tree()
        G = nx.MultiDiGraph()
        p.run_construct_tree(G, tree)
        del p
        return G

    def __init__(self, tree):
        self.cnt = self.Counter(500)
        self.PTree = self.convert_tree_from_pstree(tree)
        self.RGraph = copy.deepcopy(self.PTree)
        self.preprocess()

    def perf_act(self, G, attr, node, result, status, cnt):
        if status in ['creator', 'holder']:
            G.add_edge(node, result[0], key="creator")
        elif status == 'credential_comp':
            # maybe leader were unset - return the leader (by setting the state before)
            new_node = cnt.inc()
            # add child
            G.add_node(new_node)
            G.nodes[new_node].update({'pid': G.nodes[node][attr.name],
                                      'pgid': G.nodes[result[0]]['pgid'],
                                      'sid': G.nodes[result[0]]['sid'],
                                      'ppid': G.nodes[result[0]]['ppid']})
            G.nodes[new_node].update({attr.name: G.nodes[node][attr.name]})
            G.add_edge(new_node, G.nodes[result[0]]['ppid'], key='pred')
            G.add_edge(G.nodes[result[0]], new_node, key='pred')
            G.add_edge(node, new_node, key="creator")

        elif status == 'cl_only':
            new_node = cnt.inc()
            # add child
            G.add_node(new_node)
            G.nodes[new_node].update({'pid': G.nodes[node][attr.name],
                                      'pgid': G.nodes[result[0]]['pgid'],
                                      'sid': G.nodes[result[0]]['sid'],
                                      'ppid': G.nodes[result[0]]['pid']})
            new_node_attr_leader = cnt.inc()
            # add child of child -- leader of created credential
            G.add_node(new_node_attr_leader)

            G.nodes[new_node_attr_leader].update({'pid': G.nodes[node][attr.name],
                                                  'pgid': G.nodes[new_node]['pgid'],
                                                  'sid': G.nodes[new_node]['sid'],
                                                  'ppid': G.nodes[new_node]['pid']})
            G.nodes[new_node_attr_leader].update({attr.name: G.nodes[node][attr.name]})
            # append cumulatively if sid and pid_ns

            G.add_edge(G.nodes[new_node_attr_leader], G.nodes[new_node], key="pred")

        elif status == 'none' and attr.name in ['pgid', 'sid'] and G.nodes[node][attr.cl_attr]==G.nodes[node][attr.name]:
            #new_node = cnt.inc()
            # add child
            #G.add_node(new_node)
            #G.nodes[new_node].update({'pid': G.nodes[node]['pid'],
            #                          'pgid': G.nodes[node]['pgid'],
            #                          'sid': G.nodes[node]['sid'],
            #                          'ppid': G.nodes[result[0]]['pid']})
            pass

    def run(self):
        G = self.RGraph
        cnt = self.Counter(500)
        root = [x for x in G.nodes() if G.in_degree(x) == 0 or x==1][0]
        for node in nx.algorithms.dfs_preorder_nodes(G, root):
            #node_depth = len(nx.shortest_path(G, root, node)) - 1
            attr = self.attr_type('pgid','sid',2,'SI')
            result, status = self.full_comp_attr_check(G, attr.name, attr.cl_attr, node)
            self.perf_act(G, attr, node, result, status, cnt)

        return G

    def local_node_attr_check(G,attr, cl_attr, current_id, node_id): # y - candidate , G.nodes[current_id] - self
        y = G.nodes[node_id]
        res = node_id if y[attr] == G.nodes[current_id][attr] and y[cl_attr] == G.nodes[current_id][cl_attr] and y['pid'] == G.nodes[current_id][attr] else None

        if res:
            return ([res],'creator')
        else:
            res = node_id if y[attr] == G.nodes[current_id][attr] and y[cl_attr] == G.nodes[current_id][cl_attr] else None
            if res:
                return ([res], 'holder')
            else:
                res = node_id if y[cl_attr] == G.nodes[current_id][cl_attr] else None
                if res:
                    return ([res], 'cl_only')

                else:
                    return ([], 'none')

    def full_comp_attr_check(self, G,attr, cl_attr, current_id): # y - candidate , G.nodes[current_id] - self
        res = [x for x, y in G.nodes(data=True) if y[attr] == G.nodes[current_id][attr] and
                y[cl_attr] == G.nodes[current_id][cl_attr] and
               y['pid'] == G.nodes[current_id][attr]
            ]
        if len(res):
            return (res,'creator')
        else:
            res = [x for x, y in G.nodes(data=True) if y[attr] == G.nodes[current_id][attr] and
                   y[cl_attr] == G.nodes[current_id][cl_attr]
                   and not x == current_id]
            if len(res):
                return (res, 'holder')
            else:
                res = [x for x, y in G.nodes(data=True) if y['pid'] == G.nodes[current_id][attr] and
                       y[cl_attr] == G.nodes[current_id][cl_attr]
                       and not x == current_id]
                if len(res):
                    return (res, 'credential_comp')
                else:
                    res = [x for x, y in G.nodes(data=True) if y[cl_attr] == G.nodes[current_id][cl_attr]
                           and not x == current_id]
                    if len(res):
                        return (res, 'cl_only')

                    else:
                        return ([], 'none')


def get_pstree(trim_kernel=True):
    #p = ps_tree()
    #G = p.get_nx_tree()
    #save_and_draw_graph(G)
    p =ps_tree()
    r = reconstructor(p.get_tree())
    T = r.RGraph
    if trim_kernel:
        if T.has_edge(0, 1):
            T.remove_edge(0, 1)
            _c_list = [c for c in sorted(nx.weakly_connected_components(r.RGraph), key=len, reverse=True)]
            for idx, c in enumerate(_c_list):
                if 0 in c:
                    _c_list.pop(idx)
                    T.remove_nodes_from([n for n  in c])
                    break
            print(_c_list)

    return r.RGraph


if __name__ == '__main__':
    save_and_draw_graph(get_pstree())


