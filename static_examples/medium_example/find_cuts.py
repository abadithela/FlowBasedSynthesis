'''
Solving a grid layout with one intermediate node (I) using the MILP for static obstacles
for the following grid:

---------------
|T| | |I| | |T|
+-+-+-+-+-+-+-+
| | | | | | | |
+-+-+-+-+-+-+-+
|I| | |S| | |I|
---------------
'''
import sys
sys.path.append('../..')

from static_examples.solve_problem import solve_problem
from static_examples.get_graphs import get_graphs

def find_cuts():
    mazefile = 'maze.txt'

    init = [(2,2)]
    goals = [(0,0), (0,4)]
    int = [(0,2), (2,0), (2,4)]

    ints = {pos: 'int' for pos in int}

    print('S: {0}, I: {1}, T: {2}'.format(init, ints, goals))

    sys_formula = 'F(goal)'
    test_formula = 'F(int)'

    virtual, system, b_pi, virtual_sys = get_graphs(sys_formula, test_formula, mazefile, init, ints, goals)

    exit_status, annot_cuts, flow, bypass = solve_problem(virtual, system, b_pi, virtual_sys)
    print('exit status {0}'.format(exit_status))

    return annot_cuts


if __name__ == '__main__':
    find_cuts()
