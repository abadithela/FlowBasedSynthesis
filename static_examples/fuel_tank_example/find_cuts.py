'''
Solving a grid layout with two intermediate nodes (1 and 2) using the
MILP for static obstacles for the following grid:

-------------
|T| | | | |R|
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

def find_cuts(network):
    logger = setup_logger("fuel_tank_static")
    virtual, system, b_pi, virtual_sys = get_graphs_from_network(SYS_FORMULA, TEST_FORMULA, network, INIT, INTS, GOALS, logger, save_figures=True)

    exit_status, annot_cuts, flow, bypass = solve_problem_w_fuel(virtual, system, b_pi, virtual_sys, callback="exp_cb")
    print('exit status {0}'.format(exit_status))
    logger.print_runtime_latex()
    logger.print_problem_data_latex()
    logger.print_table()
    return annot_cuts


if __name__ == '__main__':
    mazefile = 'maze.txt'
    maze = FuelNetwork(mazefile)
    find_cuts(maze)
