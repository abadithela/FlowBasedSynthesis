# Simulate Runner Blocker Example
# J. Graebener
# January 2023

import sys
sys.path.append('..')
from agents import Quadruped, Tester
from maze_network import MazeNetwork
from game import Game
import os
from ipdb import set_trace as st
from utils.helper import *
from copy import deepcopy

def new_World(mazefile):
    network = MazeNetwork(mazefile)
    tester = Tester('tester', (4,2))
    sys = Quadruped('sys', (4,0), (0,4), network, tester)
    game = Game(network, sys, tester)
    return game, network, sys


def run_sim(max_timestep, filepath):
    trace=[]
    mazefile = 'maze.txt'
    game, network, sys = new_World(mazefile)
    print('sys in '+str(game.agent.s)+' and tester in '+str(game.tester.q))
    trace = save_scene(game,trace)
    game.print_game_state()
    for t in range(1,max_timestep):
        print('Timestep {}'.format(t))
        game.agent_take_step()
        game.print_game_state()
        game.example_test_strategy()
        game.print_game_state()
        # save the trace
        trace = save_scene(game,trace)
        print('sys in '+str(game.agent.s)+' and tester in '+str(game.tester.q))
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
