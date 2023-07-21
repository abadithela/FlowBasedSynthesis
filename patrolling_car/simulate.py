'''
This file calls runs the Parking Example Simulation.
Josefine Graebener
July 2023
'''
import sys
sys.path.append('..')
from agents import Car, Tester
from maze_network import MazeNetwork
from game import Game
import os
from ipdb import set_trace as st
from utils.helper import *
from copy import deepcopy

def new_World(mazefile):
    network = MazeNetwork(mazefile)
    sys = Car('sys', (4,4), (0,0), network)
    tester = Tester('tester', (4,1))
    game = Game(network, sys, tester)
    return game, network, sys


def run_sim(max_timestep, filepath):
    trace=[]
    mazefile = 'maze.txt'
    game, network, sys = new_World(mazefile)
    print('sys in '+str(game.agent.s)+' and tester in '+str(game.tester.q))
    game.print_maze_with_agents()
    trace = save_scene(game,trace)
    for t in range(1,max_timestep):
        print('Timestep {}'.format(t))
        game.agent_take_step()
        print('agent moved to '+str(game.agent.s))
        trace = save_scene(game,trace)
        game.random_test_strategy()
        print('tester moved to '+str(game.tester.q))
        # st()
        # save the trace
        trace = save_scene(game,trace)
        print('sys in '+str(game.agent.s)+' with fuel = '+str(game.agent.fuel)+' and tester in '+str(game.tester.q))
        game.print_maze_with_agents()
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
