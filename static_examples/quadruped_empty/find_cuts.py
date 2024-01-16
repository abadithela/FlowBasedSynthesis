'''
Solving a grid layout with two intermediate nodes (1 and 2) using the
MILP for static obstacles for the following grid:

-------------
|T| | | | | |
+-+-+-+-+-+-+
| | | | | |1|
+-+-+-+-+-+-+
| | | | | | |
+-+-+-+-+-+-+
|2| | | | | |
+-+-+-+-+-+-+
| | | | | | |
+-+-+-+-+-+-+
| | | | | |3|
+-+-+-+-+-+-+
|S| | | | | |
-------------
'''
import sys
sys.path.append('../..')

from static_examples.utils.solve_problem import solve_problem
from static_examples.utils.get_graphs import get_graphs
from problem_data import *

def find_cuts():
    intstr = ''.join('%s = %s, ' % (val,key) for (key,val) in INTS.items())
    print('S = '+str(INIT)+', '+intstr+' T = '+str(GOALS))

    virtual, system, b_pi, virtual_sys = get_graphs(SYS_FORMULA, TEST_FORMULA, MAZEFILE, INIT, INTS, GOALS)

    exit_status, annot_cuts, flow, bypass = solve_problem(virtual, system, b_pi, virtual_sys)
    print('exit status {0}'.format(exit_status))

    return annot_cuts


if __name__ == '__main__':
    find_cuts()
