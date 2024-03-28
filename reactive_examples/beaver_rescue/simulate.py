# Simulate Beaver Rescue Example

import sys
sys.path.append('../..')
import os

from reactive_examples.utils.custom_network import CustomNetwork
from agents import Agent
from game import Game
from reactive_examples.utils.helper import *
from problem_data import *

def new_World():
    states = ['init', 'd1', 'd2', 'int_goal', 'p1', 'p2', 'goal']
    transitions = [('init', 'd1'), ('init', 'd2'), \
    ('d1', 'd2'), ('d2', 'd1'), \
    ('p1', 'p2'), ('p2', 'p1'), \
    ('d1', 'int_goal'), ('d2', 'int_goal'),\
    ('int_goal', 'p1'), ('int_goal', 'p2'),
    ('p1', 'goal'), ('p2', 'goal'),]

    network = CustomNetwork(states, transitions)

    sys = Agent('sys', INIT[0], GOALS, network)
    game = Game(network, sys)
    return game, network, sys


def run_sim(max_timestep, filepath):
    trace=[]
    game, network, sys = new_World()
    for t in range(1,max_timestep):
        print('Timestep {}'.format(t))
        game.agent_take_step()
        game.test_strategy()
        if game.is_terminal():
            break


if __name__ == '__main__':
    max_timestep = 100
    output_dir = os.getcwd()+'/saved_traces/'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    filename = 'sim_trace.p'
    filepath = output_dir + filename
    run_sim(max_timestep, filepath)
