import io
import random
from simulator import *
from processing import *


def load_strace(inp):
    syscalls = []
    for line in [d for d in input]:
        if any(line.startsWith(item) for item in ['fork','clone','vfork','setsid','setpgid','exit']):
            syscalls.append(line)

    for line in syscalls:
        pass


def random_syscalls(API, steps=10000, sc_list=['fork', 'exit', 'setsid', 'setpgid']):
    for i in range(steps):
        self_ = API.context.sys_schedule()
        print(self_.p)
        syscall = random.choice(sc_list)
        if syscall == 'setpgid':
            first = random.choice([P.p for P in API.context.processes])
            second = random.choice([P.g for P in API.context.processes])
            ret = perform_syscall(API, syscall, [first,second])
        else:
            if syscall == "exit":
                if self_.p == 1:
                    break
            ret = perform_syscall(API, syscall, [0])

        if ret is None or ret < 0:
                print(bcolors.WARNING+"Interpretation warning on:"+bcolors. ENDC,str(i), "command:", syscall, "PID", str(self_.p),":", ret)
        API.util_ps()

    API.util_dump_log()


if __name__ == '__main__':
    API = SysAPI()
    random_syscalls(API=API, steps=100000)
