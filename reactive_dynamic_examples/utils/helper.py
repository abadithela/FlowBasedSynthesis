import sys
sys.path.append('..')
import _pickle as pickle
import os

class Scene:
    def __init__(self, timestamp, snapshot, maze):
        self.timestamp = timestamp
        self.snapshot = snapshot
        self.maze = maze

def remove_redundant_empty_sets(trans_dict):
    transition_list = []
    for key in trans_dict.keys():
        clean_transitions = []
        clean_transitions = [i for i in trans_dict[key] if i != set()]
        if clean_transitions == []:
            clean_transitions = [set()]
        for item in clean_transitions:
            transition_list.append((key[0], key[1], item))
    return transition_list

def remove_redundant_transitions(trans_list):
    trans_dict = get_trans_dict(trans_list)
    trans_list_clean = remove_redundant_empty_sets(trans_dict)
    return trans_list_clean

def get_trans_dict(trans_list):
    trans_dict = dict()
    for k, trans in enumerate(trans_list):
        transitions = []
        transitions.append(trans[2])
        if (trans[0],trans[1]) in trans_dict.keys():
            transitions = transitions + trans_dict[(trans[0],trans[1])]
        trans_dict.update({(trans[0],trans[1]): transitions})
    return trans_dict

def save_trace(filename, trace): # save the trace in pickle file for animation
    print('Saving trace in pkl file')
    with open(filename, 'wb') as pckl_file:
        pickle.dump(trace, pckl_file)

def save_scene(game, trace): # save each scene in trace
    print('Saving scene {}'.format(game.timestep))
    snapshot = {'sys': game.agent.s, 'test': game.tester.q}
    current_scene = Scene(game.timestep, snapshot, game.maze)
    trace.append(current_scene)
    game.timestep += 1
    game.trace = trace
    return trace

def load_opt_from_pkl_file():
    opt_file = os.getcwd()+'/stored_optimization_result.p'
    with open(opt_file, 'rb') as pckl_file:
        opt = pickle.load(pckl_file)
    cuts = opt['cuts']
    GD = opt['GD']
    return cuts, GD
