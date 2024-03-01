# Simulate Runner Blocker Example
# J. Graebener
# January 2023

import sys
sys.path.append('..')
from agents import Runner
from agents import Blocker
from runnerblocker_network import RunnerBlockerNetwork
from game import Game
import os
from ipdb import set_trace as st
from utils.helper import *

from copy import deepcopy

def new_World():
    sys = Runner('sys', 0, 4)
    tester = Blocker('tester', 2)
    network = RunnerBlockerNetwork([1,2,3])
    game = Game(network, sys, tester)
    return game, network, sys


def run_sim(max_timestep, filepath):
    trace=[]
    game, network, sys = new_World()
    print('sys in '+str(game.agent.s)+' and tester in '+str(game.tester.q))
    trace = save_scene(game,trace)
    for t in range(1,max_timestep):
        print('Timestep {}'.format(t))
        game.agent_take_step()
        game.random_test_strategy()
        # save the trace
        trace = save_scene(game,trace)
        print('sys in '+str(game.agent.s)+' and tester in '+str(game.tester.q))
        if game.is_terminal():
            break
    save_trace(filepath, game.trace)


if __name__ == '__main__':
    max_timestep = 10
    output_dir = os.getcwd()+'/saved_traces/'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    filename = 'sim_trace.p'
    filepath = output_dir + filename
    run_sim(max_timestep, filepath)
