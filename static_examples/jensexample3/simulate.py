# Simulate System under Test for static example

import sys
from problem_data import *
sys.path.append('../..')
import os
from components.maze_network import MazeNetwork
from static_examples.utils.agents import Quadruped
from static_examples.utils.game_static import Game
from static_examples.utils.helper import *

def new_World(mazefile):
    init_f = set()
    prog_f = set()
    safe_f = set()

    var = 'auxvar'
    init_f |= {'auxvar'}
    prog_f |= {'auxvar'}
    safe_f |= {'X(auxvar) <-> ((X(X(X(z = '+str(INT2[0][0])+' && x = '+str(INT2[0][1])+'))))) || (auxvar && !(z = '+str(INT[0][0])+' && x = '+str(INT[0][1])+'))'}
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
