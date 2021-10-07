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
