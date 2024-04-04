'''
Beaver rescue example.
The test objective is to have the quadruped visit door 1 and door 2.
Solving a grid layout with tqo intermediate nodes (1, 2) using the
MILP for reactive obstacles.
'''

import sys
sys.path.append('../..')

from reactive_examples.utils.solve_problem import solve_problem
from reactive_examples.utils.get_graphs import get_graphs_from_network
from problem_data import *
from reactive_examples.utils.plotting_utils import make_history_plots
from reactive_examples.utils.setup_logger import setup_logger
from reactive_examples.utils.custom_network import CustomNetwork


def find_cuts(network):

    intstr = ''.join('%s = %s, ' % (val,key) for (key,val) in INTS.items())
    print('S = '+str(INIT)+', '+intstr+' T = '+str(GOALS))
    logger = setup_logger("motion_primitive")
    virtual, system, b_pi, virtual_sys = get_graphs_from_network(SYS_FORMULA, TEST_FORMULA, network, INIT, INTS, GOALS, logger)

    exit_status, annot_cuts, flow, bypass, GD, SD = solve_problem(virtual, system, b_pi, virtual_sys)
    print('exit status {0}'.format(exit_status))
    logger.print_runtime_latex()
    logger.print_problem_data_latex()
    logger.print_table()
    return annot_cuts, GD, SD


if __name__ == '__main__':
    states = ['init', 'p1', 'p2', 'p3', 'jump1', 'stand1', 'stand2', 'stand3', 'lie3',\
    'd1_j', 'd1_s', 'd2_s', 'd3_s', 'd3_l', 'goal']
    transitions = [('init', 'p1'), ('init', 'p2'), ('init', 'p3'), \
    ('p1', 'jump1'), ('p1', 'stand1'), ('p2', 'stand2'), ('p3', 'stand3'), ('p3', 'lie3'), \
    ('jump1', 'd1_j'),('stand1', 'd1_s'), ('stand2', 'd2_s'), ('stand3', 'd3_s'), ('lie3', 'd3_l'), \
    ('d1_s', 'p1'), ('d1_j', 'p1'),\
    ('d2_s', 'p2'), \
    ('d3_s', 'p3'), ('d3_l', 'p3'),\
    ('p2', 'p1'), ('p3', 'p2'), ('p1', 'p2'), ('p2', 'p3'), \
    ('d1_s', 'goal'), ('d1_j', 'goal'), ('d2_s', 'goal'), ('d3_s', 'goal'),  ('d3_l', 'goal')]


    network = CustomNetwork(states, transitions)
    find_cuts(network)
