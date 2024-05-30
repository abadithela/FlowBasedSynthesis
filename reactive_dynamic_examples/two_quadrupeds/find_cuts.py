'''
Solving a grid layout with three intermediate nodes (1, 2, and 3) using the
MILP for reactive obstacles for the following grid:

-----------
|T| | | | |
+-+-+-+-+-+
|X|X| |X|1|
+-+-+-+-+-+
| | | | | |
+-+-+-+-+-+
|2|X| |X|X|
+-+-+-+-+-+
| | | | | |
+-+-+-+-+-+
|X|X| |X|3|
+-+-+-+-+-+
|S| | | | |
-----------
'''

import sys
sys.path.append('../..')

from reactive_dynamic_examples.utils.solve_problem import solve_problem
from reactive_dynamic_examples.utils.get_graphs import get_graphs
from components.plotting import make_history_plots
from problem_data import *
from reactive_dynamic_examples.utils.setup_logger import setup_logger

def find_graphs(logger = None):
    virtual, system, b_pi, virtual_sys = get_graphs(SYS_FORMULA, TEST_FORMULA, MAZEFILE, INIT, INTS, GOALS, logger)
    return virtual, system, b_pi, virtual_sys

def solve_opt(virtual, system, b_pi, virtual_sys, logger = None, excluded_sols = [], load_sol=True):
    exit_status, annot_cuts, flow, bypass, GD, SD = solve_problem(virtual, system, b_pi, virtual_sys, excluded_sols=excluded_sols)
    print('exit status {0}'.format(exit_status))
    logger.print_runtime_latex()
    logger.print_problem_data_latex()
    return annot_cuts, GD, SD

def find_cuts(logger=None):
    intstr = ''.join('%s = %s, ' % (val,key) for (key,val) in INTS.items())
    print('S = '+str(INIT)+', '+intstr+' T = '+str(GOALS))
    logger = setup_logger("two_quadruped")
    virtual, system, b_pi, virtual_sys = get_graphs(SYS_FORMULA, TEST_FORMULA, MAZEFILE, INIT, INTS, GOALS, logger)

    exit_status, annot_cuts, flow, bypass, GD, SD = solve_problem(virtual, system, b_pi, virtual_sys)
    print('exit status {0}'.format(exit_status))

    logger.print_runtime_latex()
    logger.print_problem_data_latex()
    make_history_plots(annot_cuts, GD, system.maze)
    return annot_cuts, GD, SD


if __name__ == '__main__':
    find_cuts()
