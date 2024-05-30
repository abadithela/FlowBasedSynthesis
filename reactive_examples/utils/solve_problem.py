'''
Solving the problem for the given graphs - static obstacle implementation.
'''
import sys
sys.path.append('../..')
import time
from pdb import set_trace as st
from optimization.find_bypass_flow import find_fby
from optimization.milp_reactive_gurobipy import solve_max_gurobi
from components.setup_graphs import setup_nodes_and_edges
from components.plotting import highlight_cuts, plot_flow_on_maze, plot_maze, plot_maze_new_colors, plot_flow_soln_on_maze, highlight_path
from utils.plotting_utils import make_history_plots, highlight_history_cuts

def solve_problem(virtual, system, b_pi, virtual_sys, print_solution=True, plot_results=True):
    GD, SD = setup_nodes_and_edges(virtual, virtual_sys, b_pi)

    ti = time.time()
    exit_status, ftest, d, flow = solve_max_gurobi(GD, SD)
    tf = time.time()
    del_t = tf-ti

    if exit_status == 'opt':
        fby = find_fby(GD, d)
        bypass_flow = sum([fby[j] for j in fby.keys() if j[1] in GD.sink])
        cuts = [x for x in d.keys() if d[x] >= 0.9]

        if print_solution:
            print('Cut {} edges in the virtual game graph.'.format(len(cuts)))
            print('The max flow through I is {}'.format(flow))
            print('The bypass flow is {}'.format(bypass_flow))
            for cut in cuts:
                print('Cutting {0} to {1}'.format(GD.node_dict[cut[0]], GD.node_dict[cut[1]]))

        if plot_results:
            # highlight_cuts(cuts, GD, SD, virtual, virtual_sys)
            highlight_history_cuts(cuts, GD, SD, virtual, virtual_sys)
            sys_cuts = [(GD.node_dict[cut[0]][0], GD.node_dict[cut[1]][0]) for cut in cuts]
            # plot_flow_on_maze(system.maze, [])
            # plot_flow_on_maze(system.maze, sys_cuts)
            plot_maze_new_colors(system.maze)
            highlight_path(GD, virtual, cuts)
            highlight_path(GD, virtual, [])
            annot_cuts = [(GD.node_dict[cut[0]], GD.node_dict[cut[1]]) for cut in cuts]
            bad_annot_cuts = [(((0, 1), 'q6'),((0, 2), 'q2')), (((0, 1), 'q0'), ((0, 2), 'q3')), (((1, 2), 'q7'), ((0, 2), 'q4')), (((0, 1), 'q7'), ((0, 2), 'q4'))]
            bad_cuts = [(GD.inv_node_dict[u], GD.inv_node_dict[v]) for (u,v) in bad_annot_cuts]
            
            st()
            highlight_path(GD, virtual, bad_cuts)
            highlight_cuts(bad_cuts, GD, SD, virtual, virtual_sys)
            plot_flow_soln_on_maze(system.maze, sys_cuts)


        # from ipdb import set_trace as st
        # st()
        annot_cuts = [(GD.node_dict[cut[0]], GD.node_dict[cut[1]]) for cut in cuts]
        # st()
        return exit_status, annot_cuts, flow, bypass_flow, GD, SD
    else:
        return exit_status, [], [], None, GD, SD
