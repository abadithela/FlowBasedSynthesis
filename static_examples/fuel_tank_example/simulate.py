# Simulate System under Test for static example

import sys
sys.path.append('../..')
import os

from network_fuel import FuelNetwork
from static_examples.utils.agents_w_fuel import Quadruped
from static_examples.utils.game_static_w_fuel import Game
from static_examples.utils.helper import *
from problem_data import *

def new_World(mazefile):
    network = FuelNetwork(mazefile)
    sys = Quadruped('sys', INIT[0], GOALS, network)
    game = Game(network, sys)
    return game, network, sys


def run_sim(max_timestep, filepath):
    trace=[]
    game, network, sys = new_World(MAZEFILE)
    trace = save_scene(game,trace)
    game.print_game_state()
    for t in range(1,max_timestep):
        print('Timestep {}'.format(t))
        game.agent_take_step()
        game.print_game_state()
        # save the trace
        trace = save_scene(game,trace)
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