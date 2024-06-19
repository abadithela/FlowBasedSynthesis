'''
Solving the problem for the given graphs - static obstacle implementation.
'''
import sys
sys.path.append('../..')
import time
import os

from optimization.find_bypass_flow import find_fby
from optimization.milp_static_gurobipy import solve_max_gurobi
from optimization.milp_static_w_fuel_gurobipy import solve_max_gurobi as solve_max_gurobi_w_fuel

from components.setup_graphs import setup_nodes_and_edges
from components.plotting import highlight_cuts, plot_flow_on_maze, plot_flow_on_maze_w_fuel

def solve_problem_w_fuel(virtual, system, b_pi, virtual_sys, callback = True, print_solution=True, plot_results=True, instance_logger=None, logger_runtime_dict=None):
    GD, SD = setup_nodes_and_edges(virtual, virtual_sys, b_pi)

    ti = time.time()
    exit_status, ftest, d, flow = solve_max_gurobi_w_fuel(GD, SD, callback=callback, logger=instance_logger, logger_runtime_dict=logger_runtime_dict)
    tf = time.time()
    del_t = tf-ti
    print("Time to solve opt: ", str(del_t))

    if exit_status == 'opt':
        fby = find_fby(GD, d)
        bypass_flow = sum([fby[j] for j in fby.keys() if j[1] in GD.sink])
        cuts = [x for x in d.keys() if d[x] >= 0.9]

        if print_solution:
            print('Cut {} edges in the virtual game graph.'.format(len(cuts)))
            print('The max flow through I is {}'.format(flow))
            print('The bypass flow is {}'.format(bypass_flow))
            print("Time to solve opt: ", str(del_t))
            # for cut in cuts:
                # print('Cutting {0} to {1}'.format(GD.node_dict[cut[0]], GD.node_dict[cut[1]]))

        if plot_results:
            # highlight_cuts(cuts, GD, SD, virtual, virtual_sys)
            sys_cuts = [(GD.node_dict[cut[0]][0], GD.node_dict[cut[1]][0]) for cut in cuts]
            plot_flow_on_maze_w_fuel(system.maze, sys_cuts)

        annot_cuts = [(GD.node_dict[cut[0]][0], GD.node_dict[cut[1]][0]) for cut in cuts]
        return exit_status, annot_cuts, flow, bypass_flow
    else:
        return exit_status, [], [], None


def solve_problem(virtual, system, b_pi, virtual_sys, callback = "rand_cb", print_solution=True, plot_results=True, instance_logger=None, logger_runtime_dict=None):
    GD, SD = setup_nodes_and_edges(virtual, virtual_sys, b_pi)

    ti = time.time()
    exit_status, ftest, d, flow = solve_max_gurobi(GD, SD, callback=callback, logger=instance_logger, logger_runtime_dict=logger_runtime_dict)
    tf = time.time()
    del_t = tf-ti
    print("Time to solve opt: ", str(del_t))

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
            if not os.path.exists("imgs"):
                os.makedirs("imgs")
            highlight_cuts(cuts, GD, SD, virtual, virtual_sys)
            sys_cuts = [(GD.node_dict[cut[0]][0], GD.node_dict[cut[1]][0]) for cut in cuts]
            plot_flow_on_maze(system.maze, sys_cuts)

        annot_cuts = [(GD.node_dict[cut[0]][0], GD.node_dict[cut[1]][0]) for cut in cuts]
        return exit_status, annot_cuts, flow, bypass_flow
    else:
        return exit_status, [], [], None


def solve_problem_no_logger(virtual, system, b_pi, virtual_sys, callback = "rand_cb", print_solution=True, plot_results=True):
    GD, SD = setup_nodes_and_edges(virtual, virtual_sys, b_pi)

    exit_status, ftest, d, flow = solve_max_gurobi(GD, SD, callback=callback)
    
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
            if not os.path.exists("imgs"):
                os.makedirs("imgs")
            highlight_cuts(cuts, GD, SD, virtual, virtual_sys)
            sys_cuts = [(GD.node_dict[cut[0]][0], GD.node_dict[cut[1]][0]) for cut in cuts]
            plot_flow_on_maze(system.maze, sys_cuts)

        annot_cuts = [(GD.node_dict[cut[0]][0], GD.node_dict[cut[1]][0]) for cut in cuts]
        return exit_status, annot_cuts, flow, bypass_flow
    else:
        return exit_status, [], [], None
