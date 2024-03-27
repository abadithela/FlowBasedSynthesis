'''
Solving the problem for the given graphs - static obstacle implementation.
'''
import sys
sys.path.append('../..')
import time
import _pickle as pickle

from optimization.find_bypass_flow import find_fby
from optimization.milp_reactive_gurobipy import solve_max_gurobi
from optimization.milp_augmented_mixed_gurobipy import solve_max_gurobi as solve_max_gurobi_augmented
from optimization.milp_augmented_mixed_gurobipy_w_fuel import solve_max_gurobi as solve_max_gurobi_augmented_w_fuel

from components.setup_graphs import setup_nodes_and_edges
from components.plotting import highlight_cuts, plot_flow_on_maze, make_history_plots

def solve_problem(virtual, system, b_pi, virtual_sys, print_solution=True, plot_results=True, excluded_sols = []):
    GD, SD = setup_nodes_and_edges(virtual, virtual_sys, b_pi)

    ti = time.time()
    exit_status, ftest, d, flow = solve_max_gurobi(GD, SD, excluded_sols=excluded_sols)
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
            sys_cuts = [(GD.node_dict[cut[0]][0], GD.node_dict[cut[1]][0]) for cut in cuts]
            # plot_flow_on_maze(system.maze, sys_cuts)
            make_history_plots(cuts, GD, system.maze)

        annot_cuts = [(GD.node_dict[cut[0]], GD.node_dict[cut[1]]) for cut in cuts]
        return exit_status, annot_cuts, flow, bypass_flow, GD, SD
    else:
        return exit_status, [], [], None, GD, SD

def solve_problem_augmented(virtual, system, b_pi, virtual_sys, static_area, excluded_sols = [], print_solution=True, plot_results=True):
    GD, SD = setup_nodes_and_edges(virtual, virtual_sys, b_pi)

    ti = time.time()
    exit_status, ftest, d, flow = solve_max_gurobi_augmented(GD, SD, static_area = static_area, excluded_sols=excluded_sols)
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

        annot_cuts = [(GD.node_dict[cut[0]], GD.node_dict[cut[1]]) for cut in cuts]

        return exit_status, annot_cuts, flow, bypass_flow, GD, SD
    else:
        return exit_status, [], [], None, GD, SD


def solve_problem_augmented_w_fuel(virtual, system, b_pi, virtual_sys, static_area, print_solution=True, plot_results=True, excluded_sols = []):
    GD, SD = setup_nodes_and_edges(virtual, virtual_sys, b_pi)

    ti = time.time()
    exit_status, ftest, d, flow = solve_max_gurobi_augmented_w_fuel(GD, SD, static_area = static_area, excluded_sols = excluded_sols)
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
            print(cuts)
            for cut in cuts:
                print('Cutting {0} to {1}'.format(GD.node_dict[cut[0]], GD.node_dict[cut[1]]))

        annot_cuts = [(GD.node_dict[cut[0]], GD.node_dict[cut[1]]) for cut in cuts]

        opt_dict = {'cuts': annot_cuts, 'GD': GD, 'SD': SD}
        with open('stored_optimization_result.p', 'wb') as pckl_file:
            pickle.dump(opt_dict, pckl_file)

        return exit_status, annot_cuts, flow, bypass_flow, GD, SD
    else:
        return exit_status, [], [], None, GD, SD
