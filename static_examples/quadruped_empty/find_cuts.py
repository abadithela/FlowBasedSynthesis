'''
Solving a grid layout with two intermediate nodes (1 and 2) using the
MILP for static obstacles for the following grid:

-------------
| | | | | |T|
+-+-+-+-+-+-+
|2| | | | | |
+-+-+-+-+-+-+
| | | | | | |
+-+-+-+-+-+-+
| | | | | |1|
+-+-+-+-+-+-+
|S| | | | | |
-------------
'''
import sys
sys.path.append('../..')

from static_examples.solve_problem import solve_problem
from static_examples.get_graphs import get_graphs

def find_cuts():
    mazefile = 'maze.txt'

    init = [(6,0)]
    goals = [(0,0)]
    int_1 = (1,4)
    int_2 = (3,0)
    int_3 = (5,4)

    ints = {int_1: 'int_1', int_2: 'int_2', int_3: 'int_3'}

    intstr = ''.join('%s = %s, ' % (val,key) for (key,val) in ints.items())
    print('S = '+str(init)+', '+intstr+' T = '+str(goals))

    sys_formula = 'F(goal)'
    test_formula = 'F(int_1) & F(int_2) & F(int_3)'

    virtual, system, b_pi, virtual_sys = get_graphs(sys_formula, test_formula, mazefile, init, ints, goals)

    exit_status, annot_cuts, flow, bypass = solve_problem(virtual, system, b_pi, virtual_sys)
    print('exit status {0}'.format(exit_status))

    return annot_cuts


if __name__ == '__main__':
    find_cuts()
