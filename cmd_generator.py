''' CMD & Binary generator and runner. Works on Linux since 2.6 only because of ProcFS and PID Namespaces usage '''
''' Has remote connection variant (Currently requires root on remote machine by default settings) via SSH '''
''' Default config is hardcoded in current version '''
import paramiko
import networkx as nx
from backstuff import Netconfig, tcolor, prior_topological_sort, get_inferring_syscalls

def extract_cmd_list(G):
    top_order_list = list(get_inferring_syscalls(G, prior_topological_sort(G)))
    for (u,v,k) in top_order_list:
        if k == 'follow':
            continue
        print(G.nodes[u]['pid'],'('+str(u)+')',':',k)
        # parsing of cmd is not required: it is inserted during code generation directly.
    return top_order_list


def compose_src_cpp(commands):
    mmap_init = '\tint size = ' + '1' + ' * sizeof(int);\n\tvoid *addr = mmap(0, size, PROT_READ | PROT_WRITE, MAP_SHARED | MAP_ANONYMOUS, -1, 0);\n\tprintf("Syscalls counter is MMaped at %p in %d\\n", addr, getpid());\n\tint *shared = addr;'
    line_by_line = list()
    line_by_line.append( "//This code is generated automatically by pstree reconstruction command generator. It is not recommended to change it.\n")
    line_by_line.append('#include <stdio.h>\n#include <sys/wait.h>\n#include <sys/types.h>\n#include <unistd.h>\n#include <stdlib.h>\n#include <semaphore.h>\n#include <sys/mman.h>\n#include <time.h>\n#include <pthread.h>')

    line_by_line.append("\n");
    line_by_line.append("sem_t mutex;")
    line_by_line.append("\n")
    #line_by_line.append('char *commands={')
    cmdlist = list()
    agentlist = list()
    for (cmdk, cmdv) in commands:
        cmdlist.append('"'+cmdv+'",')
        agentlist.append(''+str(cmdk)+',')
    #line_by_line.append("};\n")
    line_by_line.append("pid_t required_pid, pid;\n")
    line_by_line.append('int processes[]={')
    line_by_line += agentlist
    line_by_line.append("};\n")

    line_by_line.append('void * ps_func(void * arg) {\n'
                        'if (1) {\n'
                        '\tprintf("Getting tree at timestamp: %d\\n", (int)time(NULL));\n'
                        '\t//usleep(100);\n'
                        '\tsystem("ps xao pid,ppid,pgid,sid");\n'
                        '\t}'
                        '\n\treturn NULL;\n'
                        '}\n')

    line_by_line.append("int main() {")
    line_by_line.append('printf("Running reconstruction procedure at timestamp: %d\\n", (int)time(NULL));');
    #line_by_line.append('usleep(5000);')
    line_by_line.append("\tsem_init(&mutex, 0, 1);")
    line_by_line.append("\tpthread_t t[1];")
    line_by_line.append("\tpthread_create(t, NULL, ps_func, NULL);")
    line_by_line.append(mmap_init)
    line_by_line.append("\n\twhile (shared[0] < "+str(len(commands))+") {" )
    i=0
    for i in range(len(commands)):
        line_by_line.append("\t\trequired_pid = processes[" + str(i) + "];")
        line_by_line.append("\t\tpid = getpid();")
        line_by_line.append("\t\tif ( (pid == required_pid) && (shared[0] == "+str(i)+ ") && (shared[0] < "+str(len(commands))+") ) {")
        line_by_line.append("\t\t\tsem_wait(&mutex);")
    # execute cmd
        line_by_line.append("\t\t\tshared[0]++;")
        #line_by_line.append(
        #    '\nprintf("\t\t\tPerforming required_pid=%d pid=%d shared=%d len=%d\\n",required_pid, getpid(), shared[0]-1, ' + str(
        #        len(commands)) + ');\n')

        cmdk,cmdv = commands[i]
        line_by_line.append("\t\t\tint ret_code = "+cmdv+";")
        line_by_line.append('\t\t\tprintf("[%d] (%d/%d) Performing %d: %d=%s\\n" , (int)time(NULL), shared[0],' + str(
                len(commands)) +  ' , getpid(), ret_code,"' + cmdv + '");')
        line_by_line.append('\t\t\t//Command '+str(i))
        line_by_line.append("\t\t\tsem_post( & mutex);")
        line_by_line.append("\n\t\t}")
    line_by_line.append('\t\tfflush(stdout);')
    line_by_line.append("\t}\n\tmunmap(addr,size);\n\treturn 0;\n}")
    return line_by_line

def compile_cpp(fname, bin_name, std=" -std=C99 "):
    return exec("gcc " + fname + std + ' -o ' + bin_name + " -pthread")

def run_app(bin_name, new_ns=True):
    if new_ns:
        return exec("./run_new_ns -p " + bin_name + " & ps xao pid,ppid,pgid,sid")

def run_remotely(cmdline, host='192.168.1.100', port='22', user='osboxes', password='osboxes.org', prog_prefix=''):
    hostname = host
    port = port
    username = user
    s = paramiko.SSHClient()
    s.load_system_host_keys()
    s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ret = s.connect(hostname, port, username, password)
    except Exception as e:
        print(tcolor.RED, "Communication error:", e, tcolor.END)
        return -1
    for cmd in cmdline:
        command = cmd
        print(">>>"+tcolor.BOLD+tcolor.UNDERLINE+"Exec cmd: "+tcolor.END+tcolor.UNDERLINE+tcolor.DARKCYAN+cmd+tcolor.END+tcolor.UNDERLINE+tcolor.BOLD+" on remote host"+tcolor.END)
        (stdin, stdout, stderr) = s.exec_command(command)
        print(tcolor.BOLD+"   Output:"+tcolor.END)
        for line in stdout.readlines():
            print('\t'+line)
        print(tcolor.BOLD+"   Errors:"+tcolor.END)

        for line in stderr.readlines():
            print('\t'+tcolor.RED+line+tcolor.END)

    s.close

# test:
def test(bin_name, run_mode='remote', config=Netconfig(host='192.168.1.100', port='22', user='root', password='osboxes.org', prog_prefix='/media/sf_Downloads/ptree_dumper/')):
    G=nx.MultiDiGraph()
    G.add_node(1)
    G.add_node(2)
    G.add_edge(1,2,key='fork()')
    extract_cmd_list(G)
    od = [(1,'fork()'),(3,'setsid()')]
    listc = compose_src_cpp(od)
    #print(listc)
    with open('native_code/code.c', 'w') as f:
        for item in listc:
            f.write("%s\n" % item)

    print(tcolor.BOLD+ "program is written to " + tcolor.END + tcolor.DARKCYAN + 'native_code/code.c'+ tcolor.END + tcolor.BOLD + " you can manually check it" + tcolor.END)

    if run_mode == 'remote':
        cmdline = []
        compile_cmd = "gcc native_code/code.c -o "+ bin_name + " -pthread"
        run_cmd = "./native_code/run_new_ns -p ./"+ bin_name # + " |  ps xao pid,ppid,pgid,sid"
        print(config.prog_prefix)
        cmdline.append("uname -a")
        cmdline.append("cd " + config.prog_prefix +" && pwd && " + compile_cmd)
        cmdline.append("cd " + config.prog_prefix +" && pwd && " + run_cmd)
        print(tcolor.BOLD +
            "Trying to connect to " + tcolor.END+tcolor.DARKCYAN +config.user + "@" + config.host + ":" + config.port + tcolor.END+tcolor.BOLD+", build the binary " +tcolor.END+tcolor.DARKCYAN+ bin_name + tcolor.END+tcolor.BOLD+" and run..."+tcolor.END)
        run_remotely(cmdline, config.host, config.port, config.user, config.password, config.prog_prefix)
    else:
        compile_cpp('native_code/code.c', "native_code/tree_maker")
        run_app("native_code/tree_maker")


# perform:
def perform(G, bin_name, run_mode='remote', config=Netconfig(host='192.168.1.100', port='22', user='root', password='osboxes.org', prog_prefix='/media/sf_Downloads/ptree_dumper/')):
    od = [(G.nodes[x]['pid'],z) for (x,y,z) in list(extract_cmd_list(G))]
    listc = compose_src_cpp(od)
    print("Operations to perform:")
    print(listc)
    with open('native_code/code.c', 'w') as f:
        for item in listc:
            f.write("%s\n" % item)

    print(tcolor.BOLD+ "program is written to " + tcolor.END + tcolor.DARKCYAN + 'native_code/code.c'+ tcolor.END + tcolor.BOLD + " you can manually check it" + tcolor.END)

    if run_mode == 'remote':
        cmdline = []
        compile_cmd = "gcc native_code/code.c -o "+ bin_name + " -pthread"
        run_cmd = "./native_code/run_new_ns -p ./"+ bin_name # + " |  ps xao pid,ppid,pgid,sid"
        print(config.prog_prefix)
        cmdline.append("uname -a")
        cmdline.append("cd " + config.prog_prefix +" && pwd && " + compile_cmd)
        cmdline.append("cd " + config.prog_prefix +" && pwd && " + run_cmd)
        print(tcolor.BOLD +
            "Trying to connect to " + tcolor.END+tcolor.DARKCYAN +config.user + "@" + config.host + ":" + config.port + tcolor.END+tcolor.BOLD+", build the binary " +tcolor.END+tcolor.DARKCYAN+ bin_name + tcolor.END+tcolor.BOLD+" and run..."+tcolor.END)
        run_remotely(cmdline, config.host, config.port, config.user, config.password, config.prog_prefix)
    else:
        compile_cpp('native_code/code.c', "native_code/tree_maker")
        run_app("native_code/tree_maker")


if __name__ == '__main__':
    test(bin_name='native_code/treemaker')