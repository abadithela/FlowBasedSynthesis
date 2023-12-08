'''
Solving empty grids of different sizes with two intermediates using the MILP for reactive obstacles.
'''

import sys
sys.path.append('..')
import numpy as np
from ipdb import set_trace as st
import networkx as nx
import pdb
import time
import itertools
import matplotlib.pyplot as plt

from b_product_3_intermed import get_B_product

from optimization.find_bypass_flow import find_fby
from optimization.milp_mixed_gurobipy import solve_max_gurobi

from components.b_sys import get_B_sys
from components.transition_system import ProductTransys
from components.setup_graphs import GraphData, setup_nodes_and_edges
from components.plotting import plot_maze, plot_flow_on_maze, highlight_cuts, make_history_plots
from components.tools import synchronous_product
import _pickle as pickle
import datetime

plot_results = True
print_solution = True

def solve_instance(virtual, system, b_pi, virtual_sys, static_area):
    GD, SD = setup_nodes_and_edges(virtual, virtual_sys, b_pi)

    ti = time.time()
    exit_status, ftest, d, flow = solve_max_gurobi(GD, SD, static_area)
    tf = time.time()
    del_t = tf-ti

    fby = find_fby(GD, d)
    bypass_flow = sum([fby[j] for j in fby.keys() if j[1] in GD.sink])

    if exit_status == 'opt':
        if print_solution:
            cuts = [x for x in d.keys() if d[x] >= 0.9]
            print('Cut {} edges in the virtual game graph.'.format(len(cuts)))
            print('The max flow through I is {}'.format(flow))
            print('The bypass flow is {}'.format(bypass_flow))
            for cut in cuts:
                print('Cutting {0} to {1}'.format(GD.node_dict[cut[0]], GD.node_dict[cut[1]]))

        if plot_results:
            cuts = [x for x in d.keys() if d[x] >= 0.9]
            highlight_cuts(cuts, GD, SD, virtual, virtual_sys)
            sys_cuts = [(GD.node_dict[cut[0]][0], GD.node_dict[cut[1]][0]) for cut in cuts]

            make_history_plots(cuts, GD, system.maze)

        annot_cuts = [(GD.node_dict[cut[0]][0], GD.node_dict[cut[1]][0]) for cut in cuts]
        return exit_status, del_t, annot_cuts, flow, bypass_flow
    else:
        return exit_status, 0, [], [], None



if __name__ == '__main__':

    mazefile = 'maze.txt'

    del_ts = []

    # set S, I, T location for grid
    init = [(6,0)]
    int_1 = (5,4)
    int_2 = (3,0)
    int_3 = (1,4)
    goals = [(0,0)]

    ints = {int_1: 'int_1', int_2: 'int_2', int_3: 'int_3'}

    print("S = {0}, I1 = {1}, I2 = {2}, I3 = {3}, T = {4}".format(init, int_1, int_2, int_3, goals))

    # get system
    system = ProductTransys()
    system.construct_sys(mazefile, init, ints, goals)

    # get Buchi automata
    b_sys = get_B_sys(system.AP)
    b_pi = get_B_product()

    # get virtual sys
    virtual_sys = synchronous_product(system, b_sys)
    # get virtual product
    virtual = synchronous_product(system, b_pi)

    # st()
    total_area = [node for node in system.maze.G_single.nodes]
    reactive_area = [(k,2) for k in range(0,6)]
    static_area = [state for state in total_area if state not in reactive_area]
    # st()
    exit_status, del_t, cuts, flow, bypass = solve_instance(virtual, system, b_pi, virtual_sys, static_area)

    if exit_status == 'opt':
        print("Total time to solve opt: {0}, total flow = {1}, bypass flow = {2}".format(del_t, flow, bypass))
        del_ts.append(del_t)
    elif exit_status == 'inf':
        print('Infeasible Grid Layout')
        num_infeas = num_infeas+1
    elif exit_status == 'not solved':
        print('Not solved')
        not_solved = not_solved+1
