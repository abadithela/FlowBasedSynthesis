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
from utils.reactive_solve_problem import solve_problem as reactive_solve_problem
from utils.reactive_get_graphs import get_graphs as reactive_get_graphs
from utils.setup_logger import setup_logger, get_runtime_dict_from_log
from utils.generate_problem_data import generate_specs_and_propositions, generate_random_grid

NUM_INTS = 3 # numer of reaction specs

def set_up_reachability_problem(gridsize, num):
    obstacle_coverage = 0
    type = 'reaction'
    sys_formula, test_formula, props = generate_specs_and_propositions(type, num)
    init, ints, goals, obs = generate_random_grid(gridsize, obstacle_coverage, props)
    return sys_formula, test_formula, init, ints, goals, obs

def run_static_instance(mazefile, logger, instance_logger, gridsize, obstacle_coverage=0):
    logger_runtime_dict = logger.log[f"maze_{gridsize}"]

    sys_formula, test_formula, init, ints, goals, obs = set_up_reachability_problem(gridsize, NUM_INTS)

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
    sys_formula, test_formula, init, ints, goals, obs = set_up_reachability_problem(gridsize, NUM_INTS)

    print('S: {0}, I: {1}, T: {2}'.format(init, ints, goals))

    virtual, system, b_pi, virtual_sys = reactive_get_graphs(sys_formula, test_formula, mazefile, init, ints, goals, instance_logger, logger_runtime_dict)
    exit_status, annot_cuts, flow, bypass = reactive_solve_problem(virtual, system, b_pi, virtual_sys, print_solution=False, plot_results=False,instance_logger=instance_logger, logger_runtime_dict=logger_runtime_dict)
    logger.add_solve_status(gridsize, exit_status)
    return exit_status, init, ints, goals

def static_random_experiments(mazefiles, nruns, obs_coverage=0):

    sys_formula, test_formula, props = generate_specs_and_propositions('reaction', NUM_INTS)

    logger = setup_logger("run_60s_reaction_"+str(NUM_INTS), maze_dims=list(mazefiles.keys()), test_type="static", nruns=nruns, obs_coverage=obs_coverage)
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
    sys_formula, test_formula, props = generate_specs_and_propositions('reaction', NUM_INTS)
    logger = setup_logger("run_60s_reaction_"+str(NUM_INTS), maze_dims=list(mazefiles.keys()), test_type="reactive", nruns=nruns, obs_coverage=obs_coverage)
    logger.set_formulas(sys_formula, test_formula)

    with open("runtimes.txt", "a") as f:
        f.write(f"Starting reactive experiments. \n")

    for gridsize, mazefile in mazefiles.items():
        reactive_grids_evaluated = [] # Store grids already evaluated

        for instance in range(1, nruns+1):
            reactive_instance_logger = logger.get_instance_logger(instance, gridsize)
            feasible_static_grid = False
            static_attempts = 0

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

            if reactive_attempts >= 50:
                st()
                raise ValueError("Cannot run as many instances; increase grid size or decrease instances")
        with open("runtimes.txt", "a") as f:
            f.write(f"Completed gridsize {gridsize}. \n")

    logger.save_experiment_data()

def run_reactive_opt(virtual, system, b_pi, virtual_sys, reactive_logger, instance_logger, logger_runtime_dict):
    exit_status, annot_cuts, flow, bypass = reactive_solve_problem(virtual, system, b_pi, virtual_sys, print_solution=False, plot_results=False,instance_logger=instance_logger, logger_runtime_dict=logger_runtime_dict)
    reactive_logger.add_solve_status(gridsize, exit_status)
    return exit_status

def run_static_opt(virtual, system, b_pi, virtual_sys, static_logger, instance_logger, logger_runtime_dict):
    try:
        exit_status, annot_cuts, flow, bypass = static_solve_problem(virtual, system, b_pi, virtual_sys,print_solution=False, plot_results=False, instance_logger=instance_logger, logger_runtime_dict=logger_runtime_dict)
    except:
        st()
    static_logger.add_solve_status(gridsize, exit_status)
    return exit_status

def get_graph(static_logger, reactive_logger, gridsize, mazefile, static_instance_logger):
    static_logger_runtime_dict = static_logger.log[f"maze_{gridsize}"]
    reactive_logger_runtime_dict = reactive_logger.log[f"maze_{gridsize}"]
    sys_formula, test_formula, init, ints, goals, obs = set_up_reachability_problem(gridsize, NUM_INTS)
    print('S: {0}, I: {1}, T: {2}'.format(init, ints, goals))
    virtual, system, b_pi, virtual_sys = static_get_graphs(sys_formula, test_formula, mazefile, init, ints, goals, static_instance_logger, static_logger_runtime_dict)
    return virtual, system, b_pi, virtual_sys, static_logger_runtime_dict, reactive_logger_runtime_dict, init, ints, goals

def static_reactive_random_experiments(mazefiles, nruns, obs_coverage=0):
    sys_formula, test_formula, props = generate_specs_and_propositions('reaction', NUM_INTS)
    reactive_logger = setup_logger("run_60s_reaction_"+str(NUM_INTS), maze_dims=list(mazefiles.keys()), test_type="reactive", nruns=nruns, obs_coverage=obs_coverage)
    reactive_logger.set_formulas(sys_formula, test_formula)

    static_logger = setup_logger("run_60s_reaction_"+str(NUM_INTS), maze_dims=list(mazefiles.keys()), test_type="static", nruns=nruns, obs_coverage=obs_coverage)
    static_logger.set_formulas(sys_formula, test_formula)

    with open("runtimes.txt", "a") as f:
        f.write(f"Starting reactive experiments. \n")

    for gridsize, mazefile in mazefiles.items():
        static_grids_evaluated = [] # Store grids already evaluated so they are not repeated.
        for instance in range(1, nruns+1):
            static_instance_logger = static_logger.get_instance_logger(instance, gridsize)
            reactive_instance_logger = reactive_logger.get_instance_logger(instance, gridsize)
            virtual, system, b_pi, virtual_sys, static_logger_runtime_dict, reactive_logger_runtime_dict, init, ints, goals = get_graph(static_logger, reactive_logger, gridsize, mazefile, static_instance_logger)

            feasible_static_grid = False
            static_attempts = 0
            while not feasible_static_grid and static_attempts<50:
                exit_status_static = run_static_opt(virtual, system, b_pi, virtual_sys, static_logger, static_instance_logger, static_logger_runtime_dict)
                exit_status = run_reactive_opt(virtual, system, b_pi, virtual_sys, reactive_logger, reactive_instance_logger, reactive_logger_runtime_dict)
                grid = (init, ints, goals)
                static_attempts += 1
                if exit_status_static == 'inf':
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

    static_logger.save_experiment_data()
    reactive_logger.save_experiment_data()


if __name__ == "__main__":
    mazefiles = {3:'mazes/3x3.txt', 4: 'mazes/4x4.txt'}
    mazefiles = {5: 'mazes/5x5.txt',10: 'mazes/10x10.txt',15: 'mazes/15x15.txt',20: 'mazes/20x20.txt'}
    # mazefiles = {20: 'mazes/20x20.txt', 25: 'mazes/25x25.txt',30: 'mazes/30x30.txt', }
    mazefiles = {10: 'mazes/10x10.txt',15: 'mazes/15x15.txt',20: 'mazes/20x20.txt'}
    mazefiles = {25: 'mazes/25x25.txt'}
    nruns = 20
    obs_coverage = 0

    # with open("runtimes.txt", "a") as f:
    #     f.write(" =============================== \n")
    #     f.write(f"Starting static reaction {NUM_INTS} experiments. \n")
    #     f.write(" =============================== \n")
    # static_random_experiments(mazefiles, nruns)
    # with open("runtimes.txt", "a") as f:
    #     f.write(f"Static reaction {NUM_INTS} experiments completed. \n")
    #     f.write(" =============================== \n")
    #     f.write(" =============================== \n")
        
    # with open("runtimes.txt", "a") as f:
    #     f.write(" =============================== \n")
    #     f.write(f"Starting reactive reaction {NUM_INTS} experiments. \n")
    #     f.write(" =============================== \n")
    # reactive_random_experiments(mazefiles, nruns)
    # with open("runtimes.txt", "a") as f:
    #     f.write(f"Reactive reaction {NUM_INTS} experiments completed. \n")
    #     f.write(" =============================== \n")
    #     f.write(" =============================== \n")

    with open("runtimes.txt", "a") as f:
        f.write(" =============================== \n")
        f.write(f"Starting reactive reaction {NUM_INTS} experiments. \n")
        f.write(" =============================== \n")
    static_reactive_random_experiments(mazefiles, nruns)
    with open("runtimes.txt", "a") as f:
        f.write(f"Reactive reaction {NUM_INTS} experiments completed. \n")
        f.write(" =============================== \n")
        f.write(" =============================== \n")
    
