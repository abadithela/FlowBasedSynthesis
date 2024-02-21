import sys
sys.path.append('..')
from components.scene import Scene
import _pickle as pickle
import os
from ipdb import set_trace as st


def save_trace(filename,trace): # save the trace in pickle file for animation
    print('Saving trace in pkl file')
    with open(filename, 'wb') as pckl_file:
        pickle.dump(trace, pckl_file)

def save_scene(game,trace): # save each scene in trace
    print('Saving scene {}'.format(game.timestep))
    sys_snapshot = []
    sys_snapshot.append((game.agent.name, game.agent.s))
    current_scene = Scene(game.timestep, game.maze, sys_snapshot)
    trace.append(current_scene)
    game.timestep += 1
    game.trace = trace
    return trace
