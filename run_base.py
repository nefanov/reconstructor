import sys
import argparse
from proc_base import *
from closures import save_and_draw_graph, prepare_colors_from_range, get_pstree
import test_trees
from preprocess import preprocess_tree
from gcorr import post_corr
from cmd_generator import perform


def create_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')
    checkpoint_parser = subparsers.add_parser('ckpt')
    checkpoint_parser.add_argument('-p', '--path', default='checkpoint_tree')
    checkpoint_parser.add_argument('-f', '--format', default='txt')
    restore_parser = subparsers.add_parser('rstr')
    restore_parser.add_argument('-s', '--save', default=False)
    restore_parser.add_argument('-p', '--perform', default=False)
    restore_parser.add_argument('-t', '--tree', default=None, type=open)
    restore_parser.add_argument('-r', '--runtime', default=False)
    restore_parser.add_argument('-bn', '--bin_name', default='native_code/treemaker')
    restore_parser.add_argument('-sh', '--show', default=True)
    restore_parser.add_argument('-v', '--visualize', default=True) #per-step visualization (after each transformation)
    restore_parser.add_argument('-R', '--rearrange', default=True)
    return parser


def pipeline(T, ctx=Context(), A=[],K=[],L=[], CR=dict(), save=False, perform_actions=True,
             bin_name='native_code/treemaker', rearrange=False, color_scheme = prepare_colors_from_range()):
    ctx.colors_dict = color_scheme
    if save:
        png_name = "graph_" + str(int(time()))
        save_and_draw_graph(T, num_palette=ctx.colors_dict, save_png=save, pic_name=png_name+"tree.png",  show_graph=False)
    T=preprocess_tree(T, 'sid', creators={}, cnt=Counter(99), ctx=ctx)
    if save:
        save_and_draw_graph(T,save_png=save, num_palette=ctx.colors_dict, pic_name=png_name+"_0.png", show_graph=False)
    G=process1(T, A, K, L, CR, ctx=ctx)
    if save:
        save_and_draw_graph(G,save_png=save, num_palette=ctx.colors_dict, pic_name=png_name+"_1.png", show_graph=False)
    G=process2(G, A, K, L, CR, ctx=ctx)
    if save:
        save_and_draw_graph(G,save_png=save, num_palette=ctx.colors_dict, pic_name=png_name+"_2.png", show_graph=False)
    G=process3(G, A, K, L, CR, ctx=ctx)
    if save:
        save_and_draw_graph(G,save_png=save, num_palette=ctx.colors_dict, pic_name=png_name+"_3.png", show_graph=False)
    G=process4(G, A, K, L, CR, ctx=ctx)
    if save:
        save_and_draw_graph(G,save_png=save, num_palette=ctx.colors_dict, pic_name=png_name+"_4.png", show_graph=False)
    G=process5(G, A, K, L, CR, ctx=ctx)
    if save:
        save_and_draw_graph(G,save_png=save, num_palette=ctx.colors_dict, pic_name=png_name+"_5.png", show_graph=False)
    filter_edges = [(U, V, k) for U, V, k in G.edges(keys=True) if k == 'h']
    G.remove_edges_from(filter_edges)
    filter_edges = [(U, V, k) for U, V, k in G.
        edges(keys=True) if
                     k.startswith('parent') or k.startswith('*H*') or k.startswith('creator_')
                    or k.startswith('pre') or k.startswith('H') or k.startswith('_H') or k.startswith(
                        'h-s') or k.startswith('h-i') or k.startswith('h-r') or k.startswith('rev')
                    ]
    G.remove_edges_from(filter_edges)
    cnt = Counter(6000)
    G = post_corr(G, ctx=ctx, cnt=cnt)
    if rearrange == 1:
        print("R", rearrange)
        G = rearrange_indexes(G, 1, full_tree=True) # 1==init, then 2
    if save:
        save_and_draw_graph(G, save_png=save, num_palette=ctx.colors_dict, pic_name=png_name+"_final.png", show_graph=False)
    if perform_actions:
        perform(G, bin_name=bin_name)
    return G


def run_pipeline(source_tree, save=False, perform=False, show=True, rearrange=False):
    colors = prepare_colors_from_range()
    if source_tree == 'runtime':
        T = get_pstree()
    elif not source_tree:
        T = test_trees.test4()
    else:
        pass  # load_tree_from_file
        print("TODO loading from file...")
        return None

    G = pipeline(T, ctx=Context(), save=save, perform_actions=perform, rearrange=rearrange, color_scheme=colors)
    if show:
        save_and_draw_graph(G, num_palette=colors)
    return G


if __name__ == "__main__":
    A = K = L = []
    parser = create_parser()
    sys.argv.append("rstr") #-- delete this on release
    sys.argv.append("-p")
    sys.argv.append("1")
    sys.argv.append("-R")
    sys.argv.append("1")
    parse_ns = parser.parse_args(sys.argv[1:])
    print(parse_ns)
    rm_by_mask('pic_*')
    if parse_ns.command == "ckpt":
        pass
    else:#if parse_ns.command == "rstr":
        G = run_pipeline(parse_ns.tree, parse_ns.save, parse_ns.perform, parse_ns.show, int(parse_ns.rearrange))

