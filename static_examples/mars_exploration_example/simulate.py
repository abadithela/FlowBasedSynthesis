# Simulate System under Test for Mars exploration example

import sys
sys.path.append('../..')
import os

from network_fuel import FuelNetwork
from static_examples.utils.agents_w_fuel import Quadruped
from static_examples.utils.game_static_w_fuel import Game
from static_examples.utils.helper import *
from problem_data import *

def new_World(mazefile):
    # rewriting the [](sample -> <>dropoff) as GR1 spec to synthesize the system controller
    reduced_ICE = list(set([(ice[0]) for ice in ICE]))
    ICE_str = ''
    for sample in reduced_ICE:
        ICE_str += '(z = '+str(sample[0])+' && x = '+str(sample[1])+') || '
    ICE_str = ICE_str[:-4]
    reduced_ROCK = list(set([(rock[0]) for rock in ROCK]))
    ROCK_str = ''
    for sample in reduced_ROCK:
        ROCK_str += '(z = '+str(sample[0])+' && x = '+str(sample[1])+') || '
    ROCK_str = ROCK_str[:-4]
    reduced_DROPOFF = list(set([(dropoff[0]) for dropoff in DROPOFF]))
    DROPOFF_str = ''
    for dropoff in reduced_DROPOFF:
        DROPOFF_str += '(z = '+str(dropoff[0])+' && x = '+str(dropoff[1])+') || '
    DROPOFF_str = DROPOFF_str[:-4]

    var = []
    init_f = set()
    prog_f = set()
    safe_f = set()

    var.append('icedrop')
    init_f |= {'icedrop'}
    prog_f |= {'icedrop'}
    safe_f |= {'(X(icedrop) <-> ('+DROPOFF_str+')) || (icedrop && !('+ICE_str+'))'}

    var.append('rockdrop')
    init_f |= {'rockdrop'}
    prog_f |= {'rockdrop'}
    safe_f |= {'(X(rockdrop) <-> ('+DROPOFF_str+')) || (rockdrop && !('+ROCK_str+'))'}

    aux_formula = {'var': var, 'prog': prog_f, 'init': init_f, 'safe': safe_f}

    network = FuelNetwork(mazefile)
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
            # pass
    save_trace(filepath, game.trace)


if __name__ == '__main__':
    max_timestep = 100
    output_dir = os.getcwd()+'/saved_traces/'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    filename = 'sim_trace.p'
    filepath = output_dir + filename
    run_sim(max_timestep, filepath)
