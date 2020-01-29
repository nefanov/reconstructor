from time import time
from networkx import dfs_preorder_nodes, topological_sort, line_graph
from closures import save_and_draw_graph
import os
import glob


class Counter:
    def __init__(self, id=1000):
        self.c = id

    def get(self):
        return self.c

    def inc(self):
        self.c += 1
        return self.c


class Context:
    def __init__(self, cnt=Counter(), op_cnt=0, start_time=int(time()), per_step_show=True, colors_dict=dict()):
        self.cnt = cnt
        self.time = start_time
        self.op_cnt = op_cnt # operation counter (current count of graph transformation)
        self.per_step_show = per_step_show
        self.colors_dict = colors_dict

    def inc(self):
        self.cnt += 1

    def op_inc(self):
        self.op_cnt += 1

    def renew_time(self):
        self.time = int(time())

    def disable_per_step_show(self):
        self.per_step_show = False

    def enable_per_step_show(self):
        self.per_step_show = True

    def compose_name(self, suffix=""):
        return "pic_" + str(self.time) + "_" + str(self.op_cnt) + suffix + ".png"


def print_fig(G, ctx, suffix):
    if ctx.per_step_show:
        save_and_draw_graph(G, num_palette=ctx.colors_dict, pic_name=ctx.compose_name(suffix), show_graph=False)
        ctx.op_inc()

types = {'p': 'pid_ns',
         'g': 's',
         's': 'pid_ns',
         'pid_ns': 'pid_ns'}


classes = {'p': 'FF',
           'g': 'SI',
           's': 'HI',
           'pid_ns': 'HI'}


def get_free_cnt(cnt):
    return cnt.inc()

def get_parent(G, item):
    for (u,x,k) in G.out_edges(item, keys=True):
        if k == 'pred':
            return x

    for (u, x, k) in G.out_edges(G.nodes[item]['ppid'], keys=True):
        if k == 'h' and G.nodes[x]['ppid'] == G.nodes[u]['pid']:
            return u

    return G.nodes[item]['ppid']

def has_in_syscall(G,v):
    for (x,y,z) in list(G.in_edges(v,keys=True)):
        if (z.endswith(')')):
            return y

    return None

class Netconfig:
    def __init__(self,host='192.168.1.103', port='22', user='osboxes', password='osboxes.org',prog_prefix=''):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.prog_prefix = prog_prefix


class tcolor:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'


def rearrange_indexes(G, shift=1, full_tree=True):
    old_index = list()
    new_index = dict()
    top_order_list = list(topological_sort(line_graph(G)))
    idx = 0
    for (u, v, k) in top_order_list:
        if k == 'fork()': # v born from u
            idx += 1
            old_index.append(G.nodes[v]['pid'])
            new_index[G.nodes[v]['pid']] = idx + shift
    print(new_index, old_index)
    if full_tree:
        new_index[1] = 1

    #for idx, (u, v, k) in enumerate(top_order_list):
    for v in dfs_preorder_nodes(G):
        #print(v, ": work on ", G.nodes[v])
        for key in ['pid', 'ppid', 'sid', 'pgid']:
            try:
                G.nodes[v][key] = new_index[G.nodes[v][key]]
                #top_order_list.pop(idx)
            except KeyError:
                pass
                print("\t\t\tlog", key, G.nodes[v])
        #print(v, ": res on " , G.nodes[v])

    return G



# Get a list of all the file paths that ends with .txt from in specified directory
def rm_by_mask(prefix=""):
    fileList = glob.glob(prefix)
    # Iterate over the list of filepaths & remove each file.
    for filePath in fileList:
        try:
            os.remove(filePath)
        except:
            print("Error while deleting file : ", filePath)
