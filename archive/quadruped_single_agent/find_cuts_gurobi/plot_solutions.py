import networkx as nx
from pdb import set_trace as st
from cut_flow_single_var import solve_min
from inner_min import solve_inner_min
from construct_automata.main import get_virtual_product_graphs
from setup_graphs import GraphData
from find_bypass_flow import find_fby
from flow_constraints.plotting import highlight_cuts, plot_maze, plot_flow_on_maze, plot_flow_w_colored_cuts_on_maze
from find_cuts import setup_nodes_and_edges
import time
import matplotlib.pyplot as plt

mazefiles = {5: ["runtime_mazes/maze5.txt"],
            0: ["runtime_mazes/maze0.txt"],
            2: ["runtime_mazes/maze2.txt", "runtime_mazes/maze2c.txt", "runtime_mazes/maze2d.txt"],
            4: ["runtime_mazes/maze4.txt"],
            }

mazefiles = {
            0: ["runtime_mazes/maze4.txt"],
            }

def make_solution_plot():
    for num in mazefiles.keys():
        mazefilelist = mazefiles[num]
        for mazefile in mazefilelist:
            virtual, system, b_pi, virtual_sys = get_virtual_product_graphs(mazefile)
            GD, SD = setup_nodes_and_edges(virtual, virtual_sys, b_pi)
            ti = time.time()
            ftest, d, F, lam, mu = solve_min(GD, SD, return_lam=True)
            cuts = [x for x in d.keys() if d[x] >= 0.9]
            cuts_lam = [x for x in lam.keys() if lam[x] >= 0.9]
            fby = find_fby(GD, d)
            bypass_flow = sum([fby[j] for j in fby.keys() if j[1] in GD.sink])

            tf = time.time()
            del_t = tf - ti
            print("{0} obstacles was solved in {1} seconds".format(num, del_t))

            annot_cuts = [(GD.node_dict[cut[0]], GD.node_dict[cut[1]]) for cut in cuts]
            sys_cuts = [(GD.node_dict[cut[0]][0], GD.node_dict[cut[1]][0]) for cut in cuts]
            sys_cuts_annot = [((cut[0], q1), (cut[1], q2)) for cut in sys_cuts for q1 in virtual_sys.AP for q2 in virtual_sys.AP]

            sys_cuts_lam = [(GD.node_dict[cut[0]][0], GD.node_dict[cut[1]][0]) for cut in cuts_lam]
            sys_cuts_lam_annot = [((cut[0], q1), (cut[1], q2)) for cut in sys_cuts_lam for q1 in virtual_sys.AP for q2 in virtual_sys.AP]
            # Plot flow and cuts:
            plot_maze(system.maze)
            plot_flow_on_maze(system.maze, sys_cuts,num_int=2)
            plot_flow_on_maze(system.maze, sys_cuts_lam,num_int=2)
            st()

if __name__ == '__main__':
    make_solution_plot()