'''
Solving a grid layout with three intermediate nodes (1, 2, and 3) using the
MILP for reactive obstacles for the following grid:

-----------
| | | | | |
+-+-+-+-+-+
| | | | |R|
+-+-+-+-+-+
| | | | | |
+-+-+-+-+-+
| | | | | |
+-+-+-+-+-+
|T| | | |S|
-----------
'''

import sys
sys.path.append('../..')

from reactive_dynamic_examples.utils.solve_problem import solve_problem_augmented_w_fuel
from reactive_dynamic_examples.utils.get_graphs import get_graphs_from_network as get_graphs
from problem_data import *
from components.plotting import make_history_plots_w_fuel
from reactive_dynamic_examples.utils.helper import load_opt_from_pkl_file
from network_fuel import FuelNetwork

from pdb import set_trace as st

def find_cuts(mazefile):
    network = FuelNetwork(mazefile)
    # intstr = ''.join('%s = %s, ' % (val,key) for (key,val) in INTS.items())
    # print('S = '+str(INIT)+', '+intstr+' T = '+str(GOALS))
    virtual, system, b_pi, virtual_sys = get_graphs(SYS_FORMULA, TEST_FORMULA, network, INIT, INTS, GOALS, save_figures = True)
    # try:
        # print('Checking for the optimization results')
        # annot_cuts, GD, SD = load_opt_from_pkl_file()
        # print('Optimization results loaded successfully')
    # except:
    excluded_sols = [[(81, 54), (108, 76), (131, 102), (161, 133), (169, 146), (178, 156), (192, 173), (200, 188), (209, 208)], [(81, 54), (108, 76), (131, 102), (133, 104), (169, 146), (178, 156), (192, 173), (200, 188), (209, 208)]]
    exit_status, annot_cuts, flow, bypass, GD, SD = solve_problem_augmented_w_fuel(virtual, system, b_pi, virtual_sys, static_area=STATIC_AREA, excluded_sols = excluded_sols)
    print('exit status {0}'.format(exit_status))

    make_history_plots_w_fuel(annot_cuts, GD, system.maze)
    return annot_cuts, GD, SD


if __name__ == '__main__':
    mazefile = 'maze.txt'
    find_cuts(mazefile)
