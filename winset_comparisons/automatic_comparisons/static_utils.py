'''
Finding the graphs for the given problem data.
'''
import sys
sys.path.append('../..')
import os
import time

from components.parse_specification_product import *
from components.transition_system import ProductTransys
from components.tools import synchronous_product
from components.setup_graphs import setup_nodes_and_edges
from components.plotting import highlight_cuts, plot_flow_on_maze

from optimization.find_bypass_flow import find_fby
from optimization.milp_static_gurobipy import solve_max_gurobi

from ipdb import set_trace as st

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
            highlight_cuts(cuts, GD, SD, virtual, virtual_sys)
            sys_cuts = [(GD.node_dict[cut[0]][0], GD.node_dict[cut[1]][0]) for cut in cuts]
            plot_flow_on_maze(system.maze, sys_cuts)

        annot_cuts = [(GD.node_dict[cut[0]][0], GD.node_dict[cut[1]][0]) for cut in cuts]
        return exit_status, annot_cuts, flow, bypass_flow
    else:
        return exit_status, [], [], None

def get_graphs(sys_formula, test_formula, mazefile, init, ints, goals, obs=[], save_figures = True):
    b_sys = get_system_automaton(sys_formula)
    b_test = get_tester_automaton(test_formula)
    b_pi = get_prod_automaton(sys_formula, test_formula)

    # st()

    # get system
    system = ProductTransys()
    system.construct_sys(mazefile, init, ints, goals, obs)

    # get virtual sys
    virtual_sys = synchronous_product(system, b_sys)
    # get virtual product
    virtual = synchronous_product(system, b_pi)

    if save_figures:
        if not os.path.exists('imgs'):
            os.makedirs('imgs')
        b_test.save_plot('imgs/btest')
        b_sys.save_plot('imgs/bsys')
        b_pi.save_plot('imgs/bprod')
        virtual.plot_product_dot('imgs/virtual')
        virtual_sys.plot_product_dot('imgs/virtual_sys')

    return virtual, system, b_pi, virtual_sys
