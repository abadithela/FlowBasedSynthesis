import _pickle as pickle

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
from static_examples.utils.setup_logger import setup_logger

def find_cuts(mazefile):
    network = FuelNetwork(mazefile)
    logger = setup_logger("mars_exploration")
    virtual, system, b_pi, virtual_sys = get_graphs_from_network(SYS_FORMULA, TEST_FORMULA, network, INIT, INTS, GOALS, logger)

    exit_status, annot_cuts, flow, bypass = solve_problem_w_fuel(virtual, system, b_pi, virtual_sys, callback=False)
    print('exit status {0}'.format(exit_status))

    opt_dict = {'cuts': annot_cuts}
    with open('stored_optimization_result.p', 'wb') as pckl_file:
        pickle.dump(opt_dict, pckl_file)
        
    logger.print_runtime_latex()
    logger.print_problem_data_latex()

    return annot_cuts


if __name__ == '__main__':
    mazefile = 'maze.txt'
    find_cuts(mazefile)
