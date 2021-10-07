import sys
from simulator import *
from pstree_struct import *

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def checkpoint_full_tree_reload(API, proc_list):
    API.context.processes = []
    for proc in proc_list:
        P = Process(p=int(proc[0]), g = int(proc[1]), s = int(proc[2]), pp = int(proc[3]))
        if P.p == 1: # trick for relatively old kernels simulation
            P.g = P.s = 1

        API.context.processes.append(P)

    API.context_switch([p for p in API.context.processes if p.p is 1][-1])
    if API.context.logging == True: 
        API.util_commit_log("CHKP: checkpoint_full_tree_reload")
    return API


def checkpoint_subtree_load(API, proc_list):
    # rewrites old processes by new or append if not exist
    # saves current process as scheduled
    # also suitable for full pstree reload (but checkpoint_full_tree_load is recommended to use in this case)
    # note: there is no check of pstree attributes consistency, so be careful with this function
    for proc in proc_list:
        P = Process(p=int(proc[0]), g = int(proc[1]), s = int(proc[2]), pp = int(proc[3]))
        old_P = [p for p in API.context.processes if p.p is P.p]
        if len(old_P)>0:
            API.context.processes.remove(old_P[-1])

        if P.p == 1: # trick for relatively old kernels simulation
            P.g = P.s = 1

        API.context.processes.append(P)
        if API.context.logging == True: 
            API.util_commit_log("CHKP: checkpoint_subtree_load")

    return API




def checkpoint_dump(API):
    pass


def perform_syscall(API, callname, argv=[]):
    if callname == 'fork':
        return API.fork() 
    elif callname == 'exit':
        return API.exit(argv)
    elif callname == 'setsid':
        return API.setsid()
    elif callname == 'setpgid':
        return API.setpgid(argv)
    else:
        print(bcolors.FAIL+"Wrong call name:"+bcolors.ENDC, callname)
        return -1


def interpret(API, cmd_list=[
    {'pid':1,'action':('fork',[])},
    {'pid':2,'action':('exit',[0])}
    ]):
    
    for i, cmd in enumerate(cmd_list):
        if cmd['pid'] != API.context.self_proc:
            API.context_switch([p for p in API.context.processes if p.p is cmd['pid']][-1])
            ret = perform_syscall(API, cmd['action'][0], cmd['action'][1])
            
            if ret is None or ret < 0:
                print(bcolors.WARNING+"Interpretation warning on:"+bcolors. ENDC,str(i), "command:","PID", cmd['pid'],":", cmd['action'], "retcode ==", ret)
                 

if __name__ == '__main__':
    API=SysAPI()
    interpret(API)
    g = make_pstree(API.context.processes)
    render_pstree(g, "1.png")
    print()

    checkpoint_full_tree_reload(API, get_current_host_ps())
    API.util_ps()
