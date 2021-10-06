**Process Tree Deploy Simulator**

***General properties***
- Discrete-time (event-based)
- Only syscalls are system events (for now)
- Syscall is atomic
- Syscalls invoke sequentally
- Scheduling is provided by "context switch" simulation

***Features list***

- Context switch
- System log
- Supported syscalls: fork, exit, setsid, setpgid
