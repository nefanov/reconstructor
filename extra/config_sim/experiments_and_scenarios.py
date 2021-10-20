import io
import numpy as np
import pprint
import random
import itertools
from simulator import *
from processing import *

# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

def load_strace(inp):
    syscalls = []
    for line in [d for d in input]:
        if any(line.startsWith(item) for item in ['fork','clone','vfork','setsid','setpgid','exit']):
            syscalls.append(line)

    for line in syscalls:
        pass


def pstree_to_structured_full_repr(pslist=[]):
    API = SysAPI()
    #interpret(API)
    checkpoint_full_tree_reload(API, get_current_host_ps())
    T = make_pstree(API.context.processes)
    nodes = T.get_nodes()
    for n in nodes:
        #p = n.get_attributes("p")
        g = n.get_attributes()["g"]
        s = n.get_attributes()["s"]
        pp = n.get_attributes()["pp"]
        lg = [P for P in nodes if P.get_attributes()["g"]==P.get_attributes()["p"]==g]
        if (len(lg)>0): # process-group-leader is in pstree
           T.add_edge(pydot.Edge(lg[0], n, label="group",color="lightcoral"))
        elif  len([P for P in nodes if P.get_attributes()["p"]==g])>1: # process-group-leader is in not pstree, but there is a process with such pid
            lg = ([P for P in nodes if P.get_attributes()["p"]==g])[0]
            imn = pydot.Node(s=s,p=lg[0],g=g,pp=-1, label=str(s)+" "+str(s)+" "+str(s)+" "+str(lg[0].get_attrubutes()["pp"]))
            T.add_edge(imn, lg[0], label="g_leader_deset")
            T.add_edge(lg[0], n, label="g_leader_imn")

        else: # no such processes
            imn = pydot.Node(s=s,p=g,g=g,pp=-1, label=str(g)+" "+str(g)+" "+str(s)+" "+str(-1))
            T.add_edge(imn, n, label="g_leader_imn")
            
        ls = [P for P in nodes if P.get_attributes()["s"]==P.get_attributes()["p"]==s]
        if (len(ls)>0): # process-session-leader is in pstree
            T.add_edge(pydot.Edge(ls[0], n, label="session",color="gold"))
        else: # no such processes
            imn = pydot.Node(s=s,p=s,g=s,pp=-1, label=str(s)+" "+str(s)+" "+str(s)+" "+str(-1))
            T.add_edge(imn, n, label="s_leader_imn")
        
    return T

def random_syscalls(API, steps=10000, sc_list=['fork', 'exit', 'setsid', 'setpgid'], verbose=False):
    for i in range(steps):
        self_ = API.context.sys_schedule()
        syscall = random.choice(sc_list)
        if syscall == 'setpgid':
            first = random.choice([P.p for P in API.context.processes])
            second = random.choice([P.g for P in API.context.processes])
            ret = perform_syscall(API, syscall, [first,second])
        else:
            if syscall == "exit":
                if self_.p == 1:
                    if verbose:
                        print("Force omit for init to exit")
                    continue

            ret = perform_syscall(API, syscall, [0])

        if ret is None or ret < 0:
                print(bcolors.WARNING+"Interpretation warning on:"+bcolors. ENDC,str(i), "command:", syscall, "PID", str(self_.p),":", ret)
    API.util_ps()

    API.util_dump_log()


def rand_sysc_test(loops = 1, steps = 100):
    for i in range(loops):
        API = SysAPI()
        random_syscalls(API=API, steps=steps)
        del API

    
def isomorphism_check(G1, G2, def_checker=True):
    if def_checker:
        res = nx.is_isomorphic(G1, G2)
    else:
        #add your custom procedure
        res = False
        if not res:
            pass # set WL metric
            return res, 0
    return res, 0


def update_sync_query(query, old, new):
    new_dict = {k: v for k, v in zip(old, new)}
    for item in query:  
        for k,v in item.items():
            if v['value'] in new_dict.keys() and v['sync'] == False:
                v['value'] = new_dict[v['value']]
                v['sync'] = True
        
    return query


def permute_ps(API, verbose=True, prefix="0"):
    query, old = API.extra_return_synced_ps(verbose=False)
    new = list(np.random.permutation(old[1:]))
    new = old[:1] + new
    query = update_sync_query(query, old, new)
    API.extra_make_upload_from_synced(query, save_previous=False)
    if verbose:
        #API.util_ps()
        T = make_pstree(API.context.processes)
        render_pstree(T, prefix+".png")
    return API
    
    
def make_permutations(API, iters=100, verbose=False):
    for i in range(iters):
        if verbose:
            #API.util_ps()
            T = make_pstree(API.context.processes)
            render_pstree(T, (str)(i)+"_.png")

        printProgressBar(i + 1, iters, prefix = 'Progress:', suffix = 'Complete', length = iters)
        permute_ps(API)
        
        #if verbose:
        #    API.util_ps()


if __name__ == '__main__':
    if len(sys.argv)>=2 and sys.argv[1] == "-perm":
        API = SysAPI()
        checkpoint_full_tree_reload(API, get_current_host_ps())
        make_permutations(API,iters=100)
    else:
        psl = get_current_host_ps()
        Tstar = pstree_to_structured_full_repr(pslist=psl)
        render_pstree(Tstar, "1.png")
