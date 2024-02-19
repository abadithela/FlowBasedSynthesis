# 1/27/24
# This script finds states of the tester that should be included as safety specifications.

import sys
sys.path.append('../..')
import numpy as np
from ipdb import set_trace as st
import networkx as nx
from find_cuts import find_cuts
from optimization.feasibility_constraints import find_map_G_S
from components.maze_network import MazeNetwork

class Tester_Progress_States:
    def __init__(self, GD, SD, tester_nodes, states):
        self.GD = GD
        self.SD = SD
        self.states = states # States that the tester is a part of 
        self.tester_nodes = tester_nodes
        self.map_G_to_S = find_map_G_S(self.GD, self.SD)
        self.transient_states = []
        self.compute_transient_states()

    def compute_tester_nodes(self):
        pass

    def check_path_in_S(self,node):
        '''
        Input: node is a vertex of G. 
        Function to check whether the map of the node in S, when removed, there still is a 
        path from S.init to S.sink
        '''
        Snode = self.map_G_to_S[node]

        # Create a test graph
        Stest = nx.DiGraph()
        Stest.add_nodes_from(self.SD.nodes)
        Stest.add_edges_from(self.SD.edges)

        # Remove the blocked node
        Stest.remove_node(Snode)
        nodes = Stest.nodes
        init_states_Stest = [s for s in self.SD.init if s in nodes]
        target_states_Stest = [s for s in self.SD.acc_sys if s in nodes]
        assert init_states_Stest!=[] and target_states_Stest !=[]
        for init_st in init_states_Stest:
            for target_st in target_states_Stest:
                if nx.has_path(Stest, init_st, target_st):
                    return True
        return False

    def compute_transient_states(self):
        for node in self.tester_nodes:
            if self.check_path_in_S(node):
                state = self.GD.node_dict[node]
                self.transient_states.append(state)