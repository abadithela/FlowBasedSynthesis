'''
Solving a grid layout with three intermediate nodes (1, 2, and 3) using the
MILP for reactive obstacles for the following grid:

-----------
|2| |T|
+-+-+-+-+-+
|S| |1|
-----------
'''

import sys
sys.path.append('../..')

from static_examples.utils.solve_problem import solve_problem
from static_examples.utils.get_graphs import get_graphs
from problem_data import *
from static_examples.utils.setup_logger import setup_logger

def find_cuts():
    intstr = ''.join('%s = %s, ' % (val,key) for (key,val) in INTS.items())
    print('S = '+str(INIT)+', '+intstr+' T = '+str(GOALS))
    logger = setup_logger("simple_gridworld")
    virtual, system, b_pi, virtual_sys = get_graphs(SYS_FORMULA, TEST_FORMULA, MAZEFILE, INIT, INTS, GOALS, logger, save_figures=True)

    exit_status, annot_cuts, flow, bypass = solve_problem(virtual, system, b_pi, virtual_sys)
    print('exit status {0}'.format(exit_status))

    logger.print_runtime_latex()
    logger.print_problem_data_latex()
    logger.print_table()
    return annot_cuts


if __name__ == '__main__':
    find_cuts()
