import networkx as nx
from backstuff import *

#all named nodes (item,interm,creator etc): int index
# dot: field of node
# get_parent: index --> index


def TR1(G, item, cnt):

    parent = get_parent(G,item)
    interm=get_free_cnt(cnt)
    G.add_node(interm)
    G.nodes[interm].update({'pid': G.nodes[item]['pid'], 'ppid': G.nodes[item]['ppid'],
                            'sid': G.nodes[parent]['sid'], 'pgid': G.nodes[parent]['pgid'], 'handled': True,'addedin':'TR1'})
    G.add_edge(parent,interm,'fork()')
    G.add_edge(parent, interm, 'h')
    G.add_edge(item, interm, 'pred')
    G.add_edge(interm, item,'setsid()')

    return G

def TR2(G, item, cnt):
    parent = get_parent(G,item)
    interm = get_free_cnt(cnt)
    G.add_node(interm)
    G.nodes[interm].update({'pid':item.pid,'ppid':item.ppid,
                        'sid':parent.sid,'pgid':parent.pgid,'handled':True,'addedin':'TR2'})
    G.add_edge(parent,interm,'fork()')
    G.add_edge(parent, interm, 'h')
    G.add_edge(item, interm, 'pred')
    G.add_edge(interm, item,'setpgid(0,0)')
    return G

def TR3(G, i, x, item, cnt):
    G.remove_edge(i,x,'pred')
    interm = get_free_cnt(cnt)
    G.add_node(interm)
    G.nodes[interm].update({'pid': G.nodes[x]['pid'],
                            'pgid': G.nodes[item]['pgid'],
                            'sid': G.nodes[x]['sid'],
                            'ppid': G.nodes[x]['ppid'],
                            'handled':True,'addedin':'TR3'})
    G.add_edge(interm, x, 'pred')
    G.add_edge(i, interm, 'pred')
    G.add_edge(x, interm, 'setpgid(0,0)')
    return G


def TR4(G, PG, item, cnt):
    interm = get_free_cnt(cnt)
    G.add_node(interm)
    G.nodes[interm].update({'pid':PG[0].pid, 'pgid':get_parent(PG[0]).pgid,
                            'sid':get_parent(G,PG[0]).sid, 'ppid':get_parent(G,PG[0]), 'addedin':'TR4_1','handled':True})
    creator = get_free_cnt(cnt)
    G.add_node(creator)
    G.nodes[creator].update({'pid': PG[0].pid, 'pgid': item.pgid,
                            'sid': get_parent(G,PG[0]).sid, 'ppid': get_parent(G,PG[0]), 'addedin':'TR4_2','handled':True})

    G.add_edge(creator, interm, "pred")
    G.add_edge(interm, creator, 'setpgid(0,0)')
    G.add_edge(PG[0], creator, "pred")
    G.add_edge(PG[0],interm,'fork()')
    G.add_edge(PG[0],interm,'h')
    return G


def TR5(G,cnt,item,CR):
    forked = get_free_cnt(cnt)
    G.nodes[forked].update({'pid':item.pgid,'ppid':CR[item.sid],'sid':CR[item.sid],'pgid':CR[item.sid].pgid,'handled':True, 'addedin':'TR5_1'})
    pleader = get_free_cnt(cnt)
    G.nodes[pleader].update({'pid':item.pgid,'ppid':CR[item.sid],'sid':item.sid,'pgid':item.pid, 'handled':True, 'addedin':'TR5_2'})
    G.add_edge(CR[item.sid],forked,'h')
    G.add_edge(CR[item.sid],forked,'fork()')
    G.add_edge(forked,pleader,'setpgid(0,0)')
    G.add_edge(pleader,forked,'pred')
    return G


def TR6(G,item,interm):
    #try:
    G.remove_edge(item,interm,'pred')
    #except:
    #    pass
    return G


def TR7(G,item,need_extra_node, cnt):
    gp = get_parent(G,item)

    if need_extra_node:
        interm = get_free_cnt(cnt)
        G.add_node(interm)
        print('gp', gp, 'of',item)

        G.nodes[interm].update({'pid':G.nodes[item]['pid'],'ppid':G.nodes[item]['ppid'],
                            'sid':G.nodes[gp]['sid'],'pgid':G.nodes[gp]['pgid'], 'addedin':'TR7','handled':True})
    if G.nodes[gp]['pid'] == G.nodes[item]['pid']:
        G.add_edge(gp,item,'follow')
    return G


def TR8(G,item,interm,creator):
    G.add_edge(item, interm, 'pred') #  данным pred также можно обработать зависимости
    G.add_edge(creator,item,'setpgid('+str(G.nodes[creator]['pgid']) + ',' + str(G.nodes[item]['pid'])+')')
    return G