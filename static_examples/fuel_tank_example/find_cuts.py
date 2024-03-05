'''
Solving a grid layout with two intermediate nodes (1 and 2) using the
MILP for static obstacles for the following grid:

-------------
|T| | | | | |
+-+-+-+-+-+-+
| | | | | | |
+-+-+-+-+-+-+
| | | | | | |
+-+-+-+-+-+-+
| | | | | | |
+-+-+-+-+-+-+
|S| | | | | |
-------------
'''
import sys
sys.path.append('../..')

from static_examples.utils.solve_problem import solve_problem_w_fuel
from static_examples.utils.get_graphs import get_graphs_from_network
from problem_data import *
from network_fuel import FuelNetwork

def find_cuts(network):
    # intstr = ''.join('%s = %s, ' % (val,key) for (key,val) in INTS.items())
    # print('S = '+str(INIT)+', '+intstr+' T = '+str(GOALS))
    # network = FuelNetwork(mazefile)

    virtual, system, b_pi, virtual_sys = get_graphs_from_network(SYS_FORMULA, TEST_FORMULA, network, INIT, INTS, GOALS)

    exit_status, annot_cuts, flow, bypass = solve_problem_w_fuel(virtual, system, b_pi, virtual_sys)
    print('exit status {0}'.format(exit_status))

    return annot_cuts


if __name__ == '__main__':
    mazefile = 'maze.txt'
    find_cuts(mazefile)
