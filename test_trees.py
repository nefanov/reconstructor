import networkx as nx


def test1():
    G=nx.MultiDiGraph()
    G.add_node(1)
    #G.add_node(2)
    #G.add_node(3)
    #G.add_node(4)
    G.add_node(6)
    G.add_node(5)
    G.add_node(531)

    #G.add_edge(1, 3, 'h')
    #G.add_edge(3, 2, 'h')
    G.add_edge(1, 5, 'h')
    G.add_edge(1, 6, 'h')
    G.add_edge(1, 531, 'h')

    G.nodes[1].update({'pid':1, 'pgid':1,'sid':1,'ppid':0})
    #G.nodes[2].update({'pid':2, 'pgid':2,'sid':2,'ppid':3})
    #G.nodes[3].update({'pid':3, 'pgid':3,'sid':3,'ppid':1})
    G.nodes[5].update({'pid': 5, 'pgid': 5, 'sid': 530, 'ppid': 1})
    G.nodes[6].update({'pid':6, 'pgid':5,'sid':530,'ppid':1})
    G.nodes[531].update({'pid': 531, 'pgid': 530, 'sid': 530, 'ppid': 1})

    return G

def test2(): # chain test for upbranch
    G = nx.MultiDiGraph()
    G.add_node(1)
    G.add_node(2)
    G.add_node(4)
    G.add_node(5)

    G.add_edge(1, 2, 'h')
    G.add_edge(2, 4, 'h')
    G.add_edge(4, 5, 'h')

    G.nodes[1].update({'pid': 1, 'pgid': 1, 'sid': 1, 'ppid': 0})
    G.nodes[2].update({'pid': 2, 'pgid': 2, 'sid': 2, 'ppid': 1})
    G.nodes[4].update({'pid': 4, 'pgid': 4, 'sid': 4, 'ppid': 2})
    G.nodes[5].update({'pid': 5, 'pgid': 1, 'sid': 1, 'ppid': 4})
    return G

def test3(): # chain test for upbranch
    G = nx.MultiDiGraph()
    G.add_node(1)
    G.add_node(2)
    G.add_node(3)
    G.add_node(4)
    G.add_node(5)

    G.add_edge(1, 2, 'h')
    G.add_edge(2, 3, 'h')
    G.add_edge(3, 4, 'h')
    G.add_edge(4, 5, 'h')

    G.nodes[1].update({'pid': 1, 'pgid': 1, 'sid': 1, 'ppid': 0})
    G.nodes[2].update({'pid': 2, 'pgid': 2, 'sid': 2, 'ppid': 1})
    G.nodes[3].update({'pid': 3, 'pgid': 1, 'sid': 1, 'ppid': 2})
    G.nodes[4].update({'pid': 4, 'pgid': 4, 'sid': 4, 'ppid': 3})
    G.nodes[5].update({'pid': 5, 'pgid': 1, 'sid': 1, 'ppid': 4})
    return G

def test4(): # chain test for upbranch
    G = nx.MultiDiGraph()
    G.add_node(1)
    G.add_node(2)
    G.add_node(3)
    G.add_node(4)
    G.add_node(5)
    G.add_node(6)
    G.add_node(7)

    G.add_edge(1, 2, 'h')
    G.add_edge(2, 3, 'h')
    G.add_edge(3, 4, 'h')
    G.add_edge(4, 5, 'h')
    G.add_edge(1, 6, 'h')
    G.add_edge(6, 7, 'h')

    G.nodes[1].update({'pid': 1, 'pgid': 1, 'sid': 1, 'ppid': 0})
    G.nodes[2].update({'pid': 2, 'pgid': 2, 'sid': 2, 'ppid': 1})
    G.nodes[3].update({'pid': 3, 'pgid': 3, 'sid': 1, 'ppid': 2})
    G.nodes[4].update({'pid': 4, 'pgid': 4, 'sid': 4, 'ppid': 3})
    G.nodes[6].update({'pid': 6, 'pgid': 6, 'sid': 1, 'ppid': 1})
    G.nodes[5].update({'pid': 5, 'pgid': 6, 'sid': 1, 'ppid': 4})
    G.nodes[7].update({'pid': 7, 'pgid': 7, 'sid': 7, 'ppid': 6})
    return G

def test5():
    G = nx.MultiDiGraph()
    G.add_node(1)
    G.add_node(2)
    G.add_node(3)

    G.add_edge(1, 2, 'h')
    G.add_edge(2, 3, 'h')
    G.nodes[1].update({'pid': 1, 'pgid': 1, 'sid': 1, 'ppid': 0})
    G.nodes[2].update({'pid': 2, 'pgid': 3, 'sid': 1, 'ppid': 1})
    G.nodes[3].update({'pid': 3, 'pgid': 2, 'sid': 1, 'ppid': 2})
    return G