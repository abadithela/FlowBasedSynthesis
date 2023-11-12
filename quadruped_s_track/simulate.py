# Simulated Quadruped S track example
# J. Graebener
# Nov 2023
# Synthesizing Test Environments for LTL Specifications

import sys
sys.path.append('..')
from random import choice
import numpy as np
from agents import Quadruped
from game import Game
from components.maze_network import MazeNetwork
# from components.gridworld import GridWorld
import os
from ipdb import set_trace as st
from helper import *

from b_product_3_intermed import get_B_product
from components.b_sys import get_B_sys
from components.transition_system import ProductTransys
from components.tools import synchronous_product
from components.setup_graphs import setup_nodes_and_edges



def new_World(mazefile):
    network = MazeNetwork(mazefile)

    # set S, I, T location for grid
    init = [(6,0)]
    int_1 = (5,4)
    int_2 = (3,0)
    int_3 = (1,4)
    goals = [(0,0)]

    ints = {int_1: 'int_1', int_2: 'int_2', int_3: 'int_3'}

    network.set_int(ints)
    network.set_goal(goals)

    sys = Quadruped('sys', init[0], goals[0], network)
    # get system
    system = ProductTransys()
    system.construct_sys(mazefile, init, ints, goals)

    # get Buchi automata
    b_sys = get_B_sys(system.AP)
    b_pi = get_B_product()

    # get virtual sys
    virtual_sys = synchronous_product(system, b_sys)
    # get virtual product
    virtual = synchronous_product(system, b_pi)
    GD, SD = setup_nodes_and_edges(virtual, virtual_sys, b_pi)

    cuts = [(((2, 2), 'q10'), ((1, 2), 'q10')),
            (((6, 2), 'q0'), ((5, 2), 'q0')),
            (((3, 2), 'q11'), ((2, 2), 'q11'))] # found by the optimization

    game = Game(network, sys, GD, cuts)
    return game, network, sys


def run_sim(max_timestep, filepath):
    trace=[]
    mazefile = 'maze.txt'
    game, network, sys = new_World(mazefile)
    print('Quadruped sys in ' + str(game.agent.s))
    trace = save_scene(game,trace)
    game.print_game_state()

    for t in range(1,max_timestep):
        print('Timestep {}'.format(t))
        game.agent_take_step()
        game.print_game_state()
        game.test_strategy()
        # game.print_game_state()
        # save the trace
        trace = save_scene(game,trace)
        print('sys in ' + str(game.agent.s))
        if game.is_terminal():
            break
    save_trace(filepath, game.trace)


if __name__ == '__main__':
    max_timestep = 100
    output_dir = os.getcwd()+'/saved_traces/'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    filename = 'sim_trace.p'
    filepath = output_dir + filename
    run_sim(max_timestep, filepath)
