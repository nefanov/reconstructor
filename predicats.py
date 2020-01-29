from collections import namedtuple
def a_0(u, v):
    v=namedtuple('v', v.keys())(*v.values())
    u=namedtuple('u', u.keys())(*u.values())
    if (v.pid==u.pid): #у вершин совпадает pid.
        return True
    return False
def a_1(u, v):
    v=namedtuple('v', v.keys())(*v.values())
    u=namedtuple('u', u.keys())(*u.values())
    if (v.sid==u.sid): #является ли вершина $u$ носителем сессии $v$.
        return True
    return False
def a_2(u, v):
    v=namedtuple('v', v.keys())(*v.values())
    u=namedtuple('u', u.keys())(*u.values())
    if (v.sid==u.sid==u.pgid==u.pid):# $: является ли вершина $u$ лидером сессии $v$.
        return True
    return False

def a_3(u, v):
    v=namedtuple('v', v.keys())(*v.values())
    u=namedtuple('u', u.keys())(*u.values())
    if (v.pgid==u.pgid): #$: является ли вершина $u$ носителем группы $v$.
        return True
    return False

def a_4(u, v):
    v=namedtuple('v', v.keys())(*v.values())
    u=namedtuple('u', u.keys())(*u.values())
    if (v.pgid==u.pgid==u.pid):#$: является ли вершина $u$ лидером группы $v$.
        return True
    return False

def a_5(u, v):
    v=namedtuple('v', v.keys())(*v.values())
    u=namedtuple('u', u.keys())(*u.values())
    if (u.pgid==u.pid):#$: является ли вершина $u$ лидером группы.
        return True
    return False

def a_6(u, v):
    v=namedtuple('v', v.keys())(*v.values())
    u=namedtuple('u', u.keys())(*u.values())
    if (u.pgid==u.pid==u.sid): #$: является ли вершина $u$ лидером сессии.
        return True
    return False

def a_7(u, v):
    v=namedtuple('v', v.keys())(*v.values())
    u=namedtuple('u', u.keys())(*u.values())
    if (v.sid==u.sid  and u.pgid==v.pgid and u.pid==v.ppid): #$: является ли вершина $u$ непосредственным родителем # вершины $v$.
        return True
    return False

def a_8(u, v):
    v=namedtuple('v', v.keys())(*v.values())
    u=namedtuple('u', u.keys())(*u.values())
    if (v.sid==u.sid  and u.pgid==v.pgid and u.pid==v.ppid): #$: является ли вершина $u$ непосредственным родителем вершины $v$.
        return True
    return False

def a_9(u, v):
    v=namedtuple('v', v.keys())(*v.values())
    u=namedtuple('u', u.keys())(*u.values())
    if (v.sid==u.sid  and u.pgid==v.pgid and u.pid==v.ppid): #$: является ли вершина $u$ непосредственным родителем вершины $v$.
        return True
    return False

def a_10(u, _):
    v=namedtuple('v', _.keys())(*_.values())
    u=namedtuple('u', u.keys())(*u.values())
    if (u.sid==u.pgid): #$: находится
        return True
    return False
#ли
#вершина
#в
#группе, созданной
#при
#создании
#сессии.