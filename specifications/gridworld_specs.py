"""
File to instantiate gridworld, construct atomic propositions and formulas
Apurva Badithela
6/26/23
"""

import sys
sys.path.append("../gridworld/")
from network import MazeNetwork
import spot
import pdb
from buddy import bddtrue
spot.setup()
from itertools import chain, combinations
from collections import OrderedDict as od

def powerset(s):
    if type(s)==list:
        s = list(s)
    ps = list(chain.from_iterable(combinations(s, r) for r in range(len(s)+1)))
    return ps

class TranSys():
    def __init__(self, S, A, E, I, AP, L):
        self.S = S
        self.A = A
        self.E = E
        self.I = I
        self.AP = AP
        self.L = L

def get_maze(mazefile):
    T = MazeNetwork(mazefile)
    return T

def get_APs(maze):
    """
    Set of atomic propositions required to define a specification
    for the maze. Need not initialize all cells of the grid as APs, only 
    the relevant states to define what the agent must do.
    """
    ap = [spot.formula.ap("src"), spot.formula.ap("sink")]
    ap_dict = od() 
    ap_dict[maze.source] = ap[0]
    ap_dict[maze.goal] = ap[1]
    if maze.regions:
        for k in maze.regions.keys():
            ap.append(k)
            ap_dict[k] = maze.regions[k]
    return ap, ap_dict

def define_spec():
    fstr = "F(sink)"
    return fstr

def set_spec(fstr):
    f = spot.formula(fstr)
    return f

def construct_transition_function(maze):
    E = dict()
    for s in maze.states:
        for ns in maze.next_state_dict[s]:
            if ns[0]==s[0] + 1 and ns[1]==s[1]:
                E[(s,'e')] = ns
            elif ns[0]==s[0] - 1 and ns[1]==s[1]:
                E[(s,'w')] = ns
            elif ns[0]==s[0] and ns[1]==s[1] + 1:
                E[(s,'s')] = ns
            elif ns[0]==s[0] and ns[1]==s[1] - 1:
                E[(s,'n')] = ns
            elif ns==s:
                E[(s, 'o')] = ns
            else:
                print("Incorrect transition function")
                pdb.set_trace()
            
            if (s,'o') not in E.keys(): # System can wait
                E[(s,'o')] = s
    return E

def construct_labels(maze, AP, AP_dict):
    L = od()
    Sigma = powerset(AP)
    for s in maze.states:
        if s in AP_dict.keys():
            L[s] = AP_dict[s]
        else:
            L[s] = ()
    return L

def construct_sys(mazefile):
    maze = get_maze(mazefile)
    AP, AP_dict = get_APs(maze)
    S = maze.states
    A = ['n','s','e','w', 'o']
    E = construct_transition_function(maze)
    I = maze.source
    L = construct_labels(maze, AP, AP_dict)
    Sys = TranSys(S, A, E, I, AP, L)
    return Sys

if __name__ == "__main__":
    mazefile = "../gridworld/maze.txt"
    Sys = construct_sys(mazefile)
    pdb.set_trace()
