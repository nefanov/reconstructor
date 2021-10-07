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


***Dependencies***

- Python 3 (Tested on 3.8)
- GraphViz
- Packages: more_itertools, pydot


***HOW TO***

run *python3 runsim.py* command from terminal for start simulation example or make *import runsim* into your simulation script for API usage 
