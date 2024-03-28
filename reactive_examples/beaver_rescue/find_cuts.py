'''
Beaver rescue example.
The test objective is to have the quadruped visit door 1 and door 2.
Solving a grid layout with tqo intermediate nodes (1, 2) using the
MILP for reactive obstacles.
'''

import sys
sys.path.append('../..')
from ipdb import set_trace as st

from reactive_examples.utils.solve_problem import solve_problem
from reactive_examples.utils.get_graphs import get_graphs_from_network
from problem_data import *
from reactive_examples.utils.plotting_utils import make_history_plots
from reactive_examples.utils.setup_logger import setup_logger
from reactive_examples.utils.custom_network import CustomNetwork

def find_cuts(network):

    intstr = ''.join('%s = %s, ' % (val,key) for (key,val) in INTS.items())
    print('S = '+str(INIT)+', '+intstr+' T = '+str(GOALS))
    logger = setup_logger("simple_gridworld")
    virtual, system, b_pi, virtual_sys = get_graphs_from_network(SYS_FORMULA, TEST_FORMULA, network, INIT, INTS, GOALS, logger)

    exit_status, annot_cuts, flow, bypass, GD, SD = solve_problem(virtual, system, b_pi, virtual_sys)
    print('exit status {0}'.format(exit_status))

    return annot_cuts, GD, SD

if __name__ == '__main__':
    states = ['init', 'd1', 'd2', 'int_goal', 'p1', 'p2', 'goal']
    transitions = [('init', 'd1'), ('init', 'd2'), \
    ('d1', 'd2'), ('d2', 'd1'), \
    ('p1', 'p2'), ('p2', 'p1'), \
    ('d1', 'int_goal'), ('d2', 'int_goal'),\
    ('int_goal', 'p1'), ('int_goal', 'p2'),
    ('p1', 'goal'), ('p2', 'goal'),]

    network = CustomNetwork(states, transitions)
    find_cuts(network)
