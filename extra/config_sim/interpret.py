from simulator import *

def pick_syscall(callname):
    if callname == 'fork':
        return SysAPI.fork 
    elif callname == 'exit':
        return SysAPI.exit
    elif callname == 'setsid':
        return SysAPI.setsid
    elif callname == 'setpgid':
        return SysAPI.setpgid

    else:
        print("Wrong call name:", callname)
        return None


def interpret(API, cmd_list=[
    {'pid':1,'action':('fork',[])}, 
    ]):
    
    for cmd in cmd_list:
        if cmd['pid'] != API.context.self_proc:
            API.context_switch(cmd['pid'])
            call = pick_syscall(cmd['action'][0])
            print("debug:", call)
                 

if __name__ == '__main__':
    API=SysAPI()
    interpret(API)
