
import sys
sys.path.append('..')
import numpy as np
from ipdb import set_trace as st
import itertools
from datetime import datetime

from utils.static_solve_problem import solve_problem_no_logger
from utils.static_get_graphs import get_graph_no_logger
from utils.get_graphs import get_graphs
from utils.reactive_solve_problem import solve_problem as reactive_solve_problem
from utils.reactive_get_graphs import get_graphs as reactive_get_graphs
from utils.setup_logger import *
from utils.generate_problem_data import generate_specs_and_propositions, generate_random_grid

sys.path.append('../..')
from components.plotting import plot_flow_on_maze

NUM_INTS = 3 # number of satefy specs

def setup_instance(mazefile, gridsize, obstacle_coverage=0):
    type = 'reachability'
    sys_formula, test_formula, props = generate_specs_and_propositions(type, NUM_INTS)
    init, ints, goals, obs = generate_random_grid(gridsize, obstacle_coverage, props)
    print('S: {0}, I: {1}, T: {2}'.format(init, ints, goals))
    virtual, system, b_pi, virtual_sys = get_graph_no_logger(sys_formula, test_formula, mazefile, init, ints, goals)
    return virtual, system, b_pi, virtual_sys


def static_random_experiment(mazefile, gridsize, obstacle_coverage=0):
    virtual, system, b_pi, virtual_sys = setup_instance(mazefile, gridsize)
    exit_status, cuts, flow, bypass = solve_problem_no_logger(virtual, system, b_pi, virtual_sys,print_solution=True, plot_results=True)

    return exit_status, init, ints, goals


if __name__ == "__main__":
    mazefile = 'mazes/10x10.txt'
    gridsize = 10

    static_random_experiment(mazefile, gridsize)
