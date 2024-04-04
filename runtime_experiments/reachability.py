'''
Apurva (3/27):
Script for getting runtimes for reachability in test objective and the system objective


'''

import sys
sys.path.append('..')
import numpy as np
from ipdb import set_trace as st
import itertools
from datetime import datetime

from utils.static_solve_problem import solve_problem as static_solve_problem
from utils.static_get_graphs import get_graphs as static_get_graphs
from utils.get_graphs import get_graphs 
from utils.reactive_solve_problem import solve_problem as reactive_solve_problem
from utils.reactive_get_graphs import get_graphs as reactive_get_graphs
from utils.setup_logger import *

NUM_INTS = 1 # numer of satefy specs

def generate_random_grid(gridsize, obstacle_coverage, nint=1):
    '''
    Generate random grid depending on number of intermediates
    '''
    # get random S, I, T location
    nspecial_nodes = nint + 2 # One for source and goal, and the intermediates.
    all_states = list(itertools.product(np.arange(0,gridsize), np.arange(0,gridsize)))
    number_of_states = len(all_states)
    obsnum = np.ceil(number_of_states * obstacle_coverage/100)
    choose = int(nspecial_nodes+obsnum)
    idx = np.random.choice(len(all_states),choose,replace=False)
    # set S,I,T locations
    init = [all_states[idx[0]]]
    goals = [all_states[idx[2]]]
    inter = all_states[idx[1]]
    # set the obstacles
    obs = [all_states[idx[3+int(n)]] for n in np.arange(0,obsnum)]
    ints = {inter: 'int'}
    return init, ints, goals, obs

def generate_problem_data():
    sys_formula = 'F(goal)'
    test_formula = 'F(int)'
    return sys_formula, test_formula

def setup_instance(mazefile, logger, instance_logger, gridsize, obstacle_coverage=0):
    logger_runtime_dict = logger.log[f"maze_{gridsize}"]
    sys_formula, test_formula = generate_problem_data()
    init, ints, goals, obs = generate_random_grid(gridsize, obstacle_coverage)
    print('S: {0}, I: {1}, T: {2}'.format(init, ints, goals))
    virtual, system, b_pi, virtual_sys = static_get_graphs(sys_formula, test_formula, mazefile, init, ints, goals, instance_logger, logger_runtime_dict)
    return virtual, system, b_pi, virtual_sys


def run_static_instance(mazefile, logger, instance_logger, gridsize, obstacle_coverage=0):
    logger_runtime_dict = logger.log[f"maze_{gridsize}"]
    sys_formula, test_formula = generate_problem_data()
    init, ints, goals, obs = generate_random_grid(gridsize, obstacle_coverage)
    print('S: {0}, I: {1}, T: {2}'.format(init, ints, goals))

    virtual, system, b_pi, virtual_sys = static_get_graphs(sys_formula, test_formula, mazefile, init, ints, goals, instance_logger, logger_runtime_dict)
    try:
        exit_status, annot_cuts, flow, bypass = static_solve_problem(virtual, system, b_pi, virtual_sys,print_solution=False, plot_results=False, instance_logger=instance_logger, logger_runtime_dict=logger_runtime_dict)
    except:
        st()
    logger.add_solve_status(gridsize, exit_status)
    return exit_status, init, ints, goals

def run_reactive_instance(mazefile, logger, instance_logger, gridsize, obstacle_coverage=0):
    logger_runtime_dict = logger.log[f"maze_{gridsize}"]
    sys_formula, test_formula = generate_problem_data()
    init, ints, goals, obs = generate_random_grid(gridsize, obstacle_coverage)
    print('S: {0}, I: {1}, T: {2}'.format(init, ints, goals))

    virtual, system, b_pi, virtual_sys = reactive_get_graphs(sys_formula, test_formula, mazefile, init, ints, goals, instance_logger, logger_runtime_dict)
    exit_status, annot_cuts, flow, bypass = reactive_solve_problem(virtual, system, b_pi, virtual_sys, print_solution=False, plot_results=False,instance_logger=instance_logger, logger_runtime_dict=logger_runtime_dict)
    logger.add_solve_status(gridsize, exit_status)
    return exit_status, init, ints, goals

def static_random_experiments(mazefiles, nruns, obs_coverage=0):
    sys_formula, test_formula = generate_problem_data()

    logger = setup_logger("run_60s_reachability_"+str(NUM_INTS), maze_dims=list(mazefiles.keys()), test_type="static", nruns=nruns, obs_coverage=obs_coverage)
    logger.set_formulas(sys_formula, test_formula)
    with open("runtimes.txt", "a") as f:
        f.write(f"Starting static experiments. \n")

    for gridsize, mazefile in mazefiles.items():
        static_grids_evaluated = [] # Store grids already evaluated so they are not repeated.
        for instance in range(1, nruns+1):
            static_instance_logger = logger.get_instance_logger(instance, gridsize)
            feasible_static_grid = False
            static_attempts = 0

            while not feasible_static_grid and static_attempts<50:

                exit_status, init, ints, goals = run_static_instance(mazefile, logger, static_instance_logger, gridsize)
                grid = (init, ints, goals)
                static_attempts += 1
                if exit_status == 'inf':
                    print('Infeasible Grid Layout; repeating grid find')
                elif grid in static_grids_evaluated:
                    print('Already evaluated grid; repeating grid find')
                else:
                    static_grids_evaluated.append(grid)
                    feasible_static_grid = True

            if static_attempts == 50:
                raise ValueError("Cannot run as many instances; increase grid size or decrease instances")
        
        with open("runtimes.txt", "a") as f:
            f.write(f"Completed gridsize {gridsize}. \n")
    logger.save_experiment_data()

def reactive_random_experiments(mazefiles, nruns, obs_coverage=0):
    sys_formula, test_formula = generate_problem_data()
    logger = setup_logger("run_60s_reachability_"+str(NUM_INTS), maze_dims=list(mazefiles.keys()), test_type="reactive", nruns=nruns, obs_coverage=obs_coverage)
    logger.set_formulas(sys_formula, test_formula)
    with open("runtimes.txt", "a") as f:
        f.write("Starting reactive experiments. \n")
    for gridsize, mazefile in mazefiles.items():
        reactive_grids_evaluated = [] # Store grids already evaluated

        for instance in range(1, nruns+1):
            reactive_instance_logger = logger.get_instance_logger(instance, gridsize)
            feasible_reactive_grid = False
            reactive_attempts = 0

            while not feasible_reactive_grid and reactive_attempts<50:
                exit_status, init, ints, goals = run_reactive_instance(mazefile, logger, reactive_instance_logger, gridsize)
                grid = (init, ints, goals)
                reactive_attempts += 1
                if exit_status == 'inf':
                    print('Infeasible Grid Layout; repeating grid find')
                elif grid in reactive_grids_evaluated:
                    print('Already evaluated grid; repeating grid find')
                else:
                    reactive_grids_evaluated.append(grid)
                    feasible_reactive_grid = True

            if reactive_attempts == 50:
                raise ValueError("Cannot run as many instances; increase grid size or decrease instances")
        
        with open("runtimes.txt", "a") as f:
            f.write(f"Completed gridsize {gridsize}. \n")
  
    logger.save_experiment_data()



if __name__ == "__main__":
    # mazefiles = {3: 'mazes/3x3.txt', 4: 'mazes/4x4.txt',5: 'mazes/5x5.txt', 6: 'mazes/6x6.txt', 7: 'mazes/7x7.txt',8: 'mazes/8x8.txt', 9: 'mazes/9x9.txt',10: 'mazes/10x10.txt', 25:'mazes/25x25.txt', 50:'mazes/50x50.txt'}
    # mazefiles = {3: 'mazes/3x3.txt', 4: 'mazes/4x4.txt',5: 'mazes/5x5.txt'}
    # mazefiles = {3:'mazes/3x3.txt', 4: 'mazes/4x4.txt'}
    mazefiles= {3:'mazes/3x3.txt', 4: 'mazes/4x4.txt', 5: 'mazes/5x5.txt',10: 'mazes/10x10.txt', 15: 'mazes/15x15.txt',20: 'mazes/20x20.txt'}
    # mazefiles= {20: 'mazes/20x20.txt', 25:'mazes/25x25.txt', 30: 'mazes/30x30.txt'}

    # mazefiles = {}
    nruns = 20
    obs_coverage = 0
    with open("runtimes.txt", "a") as f:
        f.write(" =============================== \n")
        f.write(f"Starting static reachability {NUM_INTS} experiments. \n")
        f.write(" =============================== \n")

    static_random_experiments(mazefiles, nruns)
    with open("runtimes.txt", "a") as f:
        f.write(f"Static reachability {NUM_INTS} experiments completed. \n")
        f.write(" =============================== \n")
        f.write(" =============================== \n")

    with open("runtimes.txt", "a") as f:
        f.write(" =============================== \n")
        f.write(f"Starting reactive reachability {NUM_INTS} experiments. \n")
        f.write(" =============================== \n")

    reactive_random_experiments(mazefiles, nruns)
    with open("runtimes.txt", "a") as f:
        f.write(f"Reactive reachability {NUM_INTS} experiments completed. \n")
        f.write(" =============================== \n")
