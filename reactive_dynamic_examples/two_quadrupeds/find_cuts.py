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
from problem_data import *

def find_cuts():
    intstr = ''.join('%s = %s, ' % (val,key) for (key,val) in INTS.items())
    print('S = '+str(INIT)+', '+intstr+' T = '+str(GOALS))

    virtual, system, b_pi, virtual_sys = get_graphs(SYS_FORMULA, TEST_FORMULA, MAZEFILE, INIT, INTS, GOALS)

    exit_status, annot_cuts, flow, bypass, GD = solve_problem(virtual, system, b_pi, virtual_sys)
    print('exit status {0}'.format(exit_status))

    make_history_plots(annot_cuts, GD, system.maze)

    return annot_cuts, GD


if __name__ == '__main__':
    find_cuts()
