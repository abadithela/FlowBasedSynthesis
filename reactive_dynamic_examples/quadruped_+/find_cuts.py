'''
Solving a grid layout with three intermediate nodes (1, 2, and 3) using the
MILP for reactive obstacles for the following grid:

-----------
| | | | |T|
+-+-+-+-+-+
|2|X| |X| |
+-+-+-+-+-+
| | | | | |
+-+-+-+-+-+
| |X| |X|1|
+-+-+-+-+-+
|S| | | | |
-----------
'''

import sys
sys.path.append('../..')

from reactive_dynamic_examples.utils.solve_problem import solve_problem_augmented
from reactive_dynamic_examples.utils.get_graphs import get_graphs
from problem_data import *
from components.plotting import make_history_plots
from reactive_dynamic_examples.utils.helper import load_opt_from_pkl_file

def find_cuts():
    intstr = ''.join('%s = %s, ' % (val,key) for (key,val) in INTS.items())
    print('S = '+str(INIT)+', '+intstr+' T = '+str(GOALS))

    virtual, system, b_pi, virtual_sys = get_graphs(SYS_FORMULA, TEST_FORMULA, MAZEFILE, INIT, INTS, GOALS)

    try:
        print('Checking for the optimization results')
        annot_cuts, GD, SD = load_opt_from_pkl_file()
        print('Optimization results loaded successfully')
    except:
        exit_status, annot_cuts, flow, bypass, GD, SD = solve_problem_augmented(virtual, system, b_pi, virtual_sys, static_area=static_area)
        print('exit status {0}'.format(exit_status))

    make_history_plots(annot_cuts, GD, system.maze)
    return annot_cuts, GD, SD


if __name__ == '__main__':
    find_cuts()