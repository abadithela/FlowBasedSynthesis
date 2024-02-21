'''
Class tester library that stores basic atomic tester agents. 
'''

import sys
from agents import Tester
import matplotlib.pyplot as plt
import networkx as nx
from maze_network import MazeNetwork
import tulip.transys as trs
import pdb

class TesterLibrary:
    def __init__(self, mazefile):
        self.maze = self.get_maze(mazefile)
        self.library = dict()
        self.setup_basic_testers()
    
    def get_maze(self, mazefile):
        return MazeNetwork(mazefile)

    def setup_basic_testers(self):
        Tstatic = trs.FTS()
        Tstatic.states.add_from(['test0', 'test1'] )
        Tstatic.states.initial.add('test0')

        # The atomic proposition ap_test needs to map to the tester state.
        Tstatic.atomic_propositions.add_from({'ap_test'}) # ap_test corresponds to the state where tester is active. 
        Tstatic.states.add('test0', ap={'ap_test'})
        Tstatic.transitions.add('test0', 'test1')
        Tstatic.plot()
       
        self.library["static"] = Tstatic

if __name__ == "__main__":
    tlib = TesterLibrary("maze.txt")
    pdb.set_trace()


    
