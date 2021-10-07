import pydot
import csv
import io
from subprocess import PIPE, run


def make_pstree(pslist=[]):
    graph = pydot.Dot()
    for i, p in enumerate(pslist):
        graph.add_node(pydot.Node(str(p.p), label=str(p.p)+" "+str(p.g)+" "+str(p.s)+" "+str(p.pp)))
        if (p.pp != 0):
            graph.add_edge(pydot.Edge(src=str(p.pp),dst=str(p.p)))

    return graph


def render_pstree(graph, fn="1.png"):
    graph.write_png(fn)


def load_ps(i_stream):
    with i_stream as fp:
        reader = csv.reader(fp, delimiter=" ", quotechar='"')
        next(reader, None)  # skip the headers 
        return [list(filter(('').__ne__, dr)) for dr in [row for row in reader]]


def get_current_host_ps():
    output = run(["ps", "xao", "pid,pgid,sid,ppid,comm"], stdout=PIPE, stderr=PIPE, universal_newlines=True)
    return load_ps(io.StringIO(output.stdout))


def load_ps_from_fs(fn="1.txt"):
    #p g s pp name
    return load_ps(open(fn))
