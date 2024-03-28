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
    states = ['init', 'p1', 'p2', 'p3', 'jump1', 'stand1', 'stand2', 'stand3', 'lie3',\
    'd1_j', 'd1_s', 'd2_s', 'd3_s', 'd3_l', 'goal']
    transitions = [('init', 'p1'), ('init', 'p2'), ('init', 'p3'), \
    ('p1', 'jump1'), ('p1', 'stand1'), ('p2', 'stand2'), ('p3', 'stand3'), ('p3', 'lie3'), \
    ('jump1', 'd1_j'),('stand1', 'd1_s'), ('stand2', 'd2_s'), ('stand3', 'd3_s'), ('lie3', 'd3_l'), \
    ('d1_s', 'p1'), ('d1_j', 'p1'),\
    ('d2_s', 'p2'), \
    ('d3_s', 'p3'), ('d3_l', 'p3'),\
    ('p2', 'p1'), ('p3', 'p2'), ('p1', 'p2'), ('p2', 'p3'), \
    ('d1_s', 'goal'), ('d1_j', 'goal'), ('d2_s', 'goal'), ('d3_s', 'goal'),  ('d3_l', 'goal')]


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
