# Simulate
# J. Graebener
# January 2024
import sys
sys.path.append('../..')
from network_fuel import FuelNetwork
from reactive_dynamic_examples.utils.game import Game
from problem_data import *

from agents import Quadruped, Tester
from utils.game import Game
import os
from ipdb import set_trace as st
from utils.helper import *
from reactive_dynamic_examples.utils.setup_logger import setup_logger

def new_World(mazefile):
    network = FuelNetwork(mazefile)
    network.set_int(INTS)
    system_init = {"z": 5, "x": 5, "f": MAX_FUEL}
    tester_init = {"z": 5, "x": 2}
    tester = Tester("tester", system_init, tester_init, network)
    sys = Quadruped("sys", system_init, (5,0), network, tester_init)
    logger = setup_logger("patrol_car")
    game = Game(network, sys, tester, logger)

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
        game.agent_take_step_augmented_fuel()
        game.print_game_state()
        game.tester_take_step()
        game.print_game_state()
        # save the trace
        trace = save_scene(game,trace)

        print('sys in '+str(game.agent.s)+' and tester in '+str(game.tester.q))
        if game.is_terminal():
            break
    save_trace(filepath, game.trace)


if __name__ == '__main__':
    max_timestep = 40
    output_dir = os.getcwd()+'/saved_traces/'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    filename = 'sim_trace.p'
    filepath = output_dir + filename
    run_sim(max_timestep, filepath)
