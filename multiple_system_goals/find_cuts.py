import sys
sys.path.append('..')
import numpy as np
from ipdb import set_trace as st
import networkx as nx
import pdb
import os
# from flow_constraints.optimization import solve_bilevel
# from cut_flow_fcns_milp import solve_min
# from flow_constraints.construct_graphs import sys_test_sync
from flow_constraints.setup_graphs import GraphData, setup_nodes_and_edges
from flow_constraints.plotting import plot_maze, plot_flow_on_maze
from optimization.find_bypass_flow import find_fby
import time

from components.tools import synchronous_product
from milp_static_gurobipy import solve_max_gurobi

from components.parse_specification_product import *
from components.transition_system import ProductTransys
from components.plotting import plot_maze, plot_solutions, highlight_cuts, plot_flow_on_maze


#
# def highlight_cuts(cuts, GD, SD, virtual, virtual_sys):
#     annot_cuts = [(GD.node_dict[cut[0]], GD.node_dict[cut[1]]) for cut in cuts]
#     sys_cuts = [(GD.node_dict[cut[0]][0], GD.node_dict[cut[1]][0]) for cut in cuts]
#     sys_cuts_annot = [((cut[0], q1), (cut[1], q2)) for cut in sys_cuts for q1 in virtual_sys.AP for q2 in virtual_sys.AP]
#
#     virtual.plot_with_highlighted_edges(annot_cuts, "imgs/virtual_with_cuts")
#     virtual_sys.plot_with_highlighted_edges(sys_cuts_annot, "imgs/virtual_sys_with_cuts")

plot_results = True
print_solution = True

def solve_instance(virtual, system, b_pi, virtual_sys):
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
            plot_maze(system.maze, sys_cuts)

        annot_cuts = [(GD.node_dict[cut[0]][0], GD.node_dict[cut[1]][0]) for cut in cuts]
        return exit_status, annot_cuts, flow, bypass_flow
    else:
        return exit_status, [], [], None

def find_cuts(mazefile):

    init = [(2,2)]
    goal1 = (0,0)
    goal2 = (0,4)
    int = (0,2)
    goals = [(2,0), (2,4)]

    ints = {goal1: 'goal1', goal2: 'goal2', int: 'int'}

    # obs = [all_states[idx[3+int(n)]] for n in np.arange(0,obsnum)]
    # ints = {gold: 'gold', bank: 'bank'}

    sys_formula = 'F(goal1) & F(goal2) & F(goal)'
    test_formula = 'F(int)'

    b_sys = get_system_automaton(sys_formula)
    b_test = get_tester_automaton(test_formula)
    b_pi = get_prod_automaton(sys_formula, test_formula)

    # get system
    system = ProductTransys()
    system.construct_sys(mazefile, init, ints, goals)

    if not os.path.exists('imgs'):
        os.makedirs('imgs')
    b_test.save_plot('imgs/btest')
    b_sys.save_plot('imgs/bsys')
    b_pi.save_plot('imgs/bprod')

    # get virtual sys
    virtual_sys = synchronous_product(system, b_sys)
    # get virtual product
    virtual = synchronous_product(system, b_pi)

    virtual.plot_product_dot('imgs/virtual')
    virtual_sys.plot_product_dot('imgs/virtual_sys')

    exit_status, annot_cuts, flow, bypass = solve_instance(virtual, system, b_pi, virtual_sys)
    print('exit status {0}'.format(exit_status))



if __name__ == '__main__':
    mazefile = 'maze.txt'
    find_cuts(mazefile)
