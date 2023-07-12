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

class TranSys():
    def __init__(self, S=None, A=None, E=None, I=None, AP=None, L=None):
        self.S = S
        self.A = A
        self.E = E
        self.I = I
        self.AP = AP
        self.L = L
    
class System(TranSys):
    def __init__(self, S=None, A=None, E=None, I=None, AP=None, L=None):
        super().__init__(S,A,E,I,AP,L)
        # =============== Attributes: ============== #
        self.AP_dict = None
        self.Sigma=None
        self.maze = None
        self.f = None # Formula

    def get_maze(self, mazefile):
        self.maze = MazeNetwork(mazefile)


    def get_APs(self):
        """
        Set of atomic propositions required to define a specification
        for the maze. Need not initialize all cells of the grid as APs, only 
        the relevant states to define what the agent must do.
        """
        self.AP = [spot.formula.ap("src"), spot.formula.ap("sink")]
        self.AP_dict = od() 
        self.AP_dict[self.maze.source] = self.AP[0]
        self.AP_dict[self.maze.goal] = self.AP[1]
        if self.maze.regions:
            for k in self.maze.regions.keys():
                self.AP.append(k)
                self.AP_dict[k] = self.maze.regions[k]

    def define_spec(self):
        fstr = "F(sink)"
        return fstr

    def set_spec(self):
        fstr = self.define_spec()
        self.f = spot.formula(fstr)
    
    def construct_transition_function(self):
        self.E = dict()
        for s in self.maze.states:
            for ns in self.maze.next_state_dict[s]:
                if ns[0]==s[0] + 1 and ns[1]==s[1]:
                    self.E[(s,'e')] = ns
                elif ns[0]==s[0] - 1 and ns[1]==s[1]:
                    self.E[(s,'w')] = ns
                elif ns[0]==s[0] and ns[1]==s[1] + 1:
                    self.E[(s,'s')] = ns
                elif ns[0]==s[0] and ns[1]==s[1] - 1:
                    self.E[(s,'n')] = ns
                elif ns==s:
                    self.E[(s, 'o')] = ns
                else:
                    print("Incorrect transition function")
                    pdb.set_trace()
                if (s,'o') not in self.E.keys(): # System can wait
                    self.E[(s,'o')] = s

    def construct_labels(self):
        self.L = od()
        self.Sigma = powerset(self.AP)
        for s in self.maze.states:
            if s in self.AP_dict.keys():
                self.L[s] = self.AP_dict[s]
            else:
                self.L[s] = ()
    
    def construct_sys(self, mazefile):
        self.get_maze(mazefile)
        self.get_APs()
        self.S = self.maze.states
        self.A = ['n','s','e','w', 'o']
        self.construct_transition_function()
        self.I = self.maze.source
        self.construct_labels()
        self.set_spec()

    def add_intermediate_nodes(self):
        self.AP.append(spot.formula.ap("int")) # Append intermed
        self.AP_dict[(2,2)] = self.AP[2]
        self.construct_labels()

def powerset(s):
    if type(s)==list:
        s = list(s)
    ps = list(chain.from_iterable(combinations(s, r) for r in range(len(s)+1)))
    return ps

if __name__ == "__main__":
    mazefile = "../gridworld/maze.txt"
    system = System()
    system.construct_sys(mazefile)
    pdb.set_trace()
