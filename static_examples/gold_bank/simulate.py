# Simulate System under Test for static example

import sys
sys.path.append('../..')
import os
from ipdb import set_trace as st
from copy import deepcopy

from components.maze_network import MazeNetwork
from static_examples.utils.agents import Quadruped
from static_examples.utils.game_static import Game
from static_examples.utils.helper import *
from problem_data import *

def new_World(mazefile):
    # rewriting the [](gold -> <>bank) as GR1 spec to synthesize the system controller
    var = 'reachbank'
    init_f = 'reachbank'
    prog_f = 'reachbank'
    safe_f = '(X(reachbank) <-> (z = '+str(BANK[0])+' && x = '+str(BANK[1])+')) || (reachbank && !(z = '+str(GOLD[0])+' && x = '+str(GOLD[1])+'))'
    aux_formula = {'var': var, 'prog': prog_f, 'init': init_f, 'safe': safe_f}
    network = MazeNetwork(mazefile)
    sys = Quadruped('sys', INIT[0], GOALS, network, aux_formula = aux_formula)
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
