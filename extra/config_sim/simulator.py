class SysContext:
    def __init__(self, processes=[], groups=[], sessions=[], init_pid=1, syslog=[], logging=True):
        self.processes = processes
        self.groups = groups
        self.sessions = sessions
        self.last_pid = 1
        self.init_pid = init_pid
        self.syslog = syslog
        self.logging = logging

    def system_start(self):
        init = Process()
        self.processes.append(init)
        return

    def sys_fork(self, caller_proc):
        proc_pids = set(sorted(set([P.p for P in self.processes])))
        if len(proc_pids)>=2**16-1:
            return -1
        while self.last_pid in proc_pids:
            self.last_pid=(self.last_pid + 1) % (2**16-1)
        self.processes.append(Process(p=self.last_pid, g=caller_proc.g, s=caller_proc.s, pp=caller_proc.p))
        return self.last_pid

    def sys_exit(self, caller_proc, exit_code=0):
        if caller_proc in self.processes:
            caller_proc.exit_code = exit_code
            self.processes.remove(caller_proc)
        else:
            return -1
            
        for proc in self.processes:
            if proc.pp == caller_proc.p:
                proc.pp = self.init_pid
        

class SysAPI:
    def __init__(self, sc=SysContext(), fromstart=True):
        self.context = sc
        if fromstart:
            self.context.system_start()
        
        self.self_proc = self.context.processes[0]

    def fork(self):
        retcode = self.context.sys_fork(self.self_proc)
        if (self.context.logging):
            self.util_commit_log(str(self.self_proc.p)+" : fork() : "+"retcode = "+str(retcode))
        return retcode

    def exit(self, exit_code=0):
        retcode = self.context.sys_exit(self.self_proc)
        if (self.context.logging):
            self.util_commit_log(str(self.self_proc.p)+" : exit("+str(exit_code)+") : "+"retcode = "+str(retcode))
        return retcode

    def context_switch(self, sp):
        self.self_proc = sp

    def util_enable_log(self):
        self.context.logging = True

    def util_disable_log(self):
        self.context.logging = False

    def util_dump_log(self):
        print("System event log:\n# :PID:\tEvent")
        for i, s in enumerate(self.context.syslog):
            print(i,":", s)

    def util_clean_log(self):
        self.context.syslog=list()

    def util_commit_log(self, event):
        self.context.syslog.append(event)

    def util_ps(self):
        print("PID\tPGID\tSID\tPPID\n------------------------------")
        query = [str(P.p)+"\t"+str(P.g)+"\t"+str(P.s)+"\t"+str(P.pp) for P in self.context.processes]
        for q in query:
            print(q)
        print("------------------------------")

        


class Process:
    def __init__(self, p=1, g=1, s=1, pp=0):
        self.p = p
        self.g = g
        self.s = s
        self.pp = pp
        self.exit_code = 0

    
if __name__ == '__main__':
    API = SysAPI()
    API.fork()
    API.context_switch(API.context.processes[1])
    API.fork()
    API.util_ps()
    API.exit()
    API.util_ps()
    API.util_dump_log()
