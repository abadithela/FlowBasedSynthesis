# File to parse optimization constraints from the output of the optimization
import sys
sys.path.append('..')
import numpy as np
from ipdb import set_trace as st
import networkx as nx
import find_cuts_two_flows.find_cuts as find_cuts
from construct_automata.main import quad_test_sync
import find_cuts_two_flows.feasibility_constraints as feasibility_constraints 
from synthesize_tester_from_constraints import Quadruped_Tester
from maze_network import MazeNetwork

class FindConstraint:
    def __init__(self):
        virtual, system, b_pi, virtual_sys = quad_test_sync()
        self.GD, self.S = find_cuts.setup_nodes_and_edges(virtual, virtual_sys, b_pi)
        # self.cuts, self.flow, self.bypass = find_cuts.call_pyomo(self.GD, self.S)
        self.cuts = [(34, 50), (44, 28)]
        self.get_map_G_to_S()
        self.cuts_to_blocked_states()
        
    def get_map_G_to_S(self):
        self.map_G_to_S = feasibility_constraints.find_map_G_S(self.GD, self.S)

    def check_path_in_S(self,node):
        '''
        Input: node is a vertex of G. 
        Function to check whether the map of the node in S, when removed, there still is a 
        path from S.init to S.sink
        '''
        Snode = self.map_G_to_S[node]

        # Create a test graph
        Stest = nx.DiGraph()
        Stest.add_nodes_from(self.S.nodes)
        Stest.add_edges_from(self.S.edges)

        # Remove the blocked node
        Stest.remove_node(Snode)
        nodes = Stest.nodes
        init_states_Stest = [s for s in self.S.init if s in nodes]
        target_states_Stest = [s for s in self.S.acc_sys if s in nodes]
        assert init_states_Stest!=[] and target_states_Stest !=[]
        for init_st in init_states_Stest:
            for target_st in target_states_Stest:
                if nx.has_path(Stest, init_st, target_st):
                    return True
        return False

    def cuts_to_blocked_states(self):
        self.blocked_states = []
        for edge_cut in self.cuts:
            u, v = edge_cut
            exist_path_u = self.check_path_in_S(u)
            exist_path_v = self.check_path_in_S(v)
            if exist_path_u:
                self.blocked_states.append(u)
            elif exist_path_v:
                self.blocked_states.append(v)
            else:
                print("Cannot place static obstacle. Must constrain edge instead")
                st()

    def parse_cuts_to_states(self):
        self.cuts_to_blocked_states()
        # With reactive obstacles, implement code here to convert blocked states to system and tester states. This
        # would require reasoning over Bpi.
        constraints_i1 = [((4,1),(3,2)), ((4,2),(3,2)), ((4,3),(3,2)), ((4,4), (3,2)), ((2,2),(1,2))]
        constraints_i2 = [((4,2),(3,2)), ((2,2),(1,2)), ((2,3),(1,2))]
        return constraints_i1, constraints_i2

if __name__ == "__main__":
    mazefile = 'maze.txt'
    maze = MazeNetwork(mazefile)
    opt_constr = FindConstraint()
    constraints_i1, constraints_i2 = opt_constr.parse_cuts_to_states()
    quadruped = Quadruped_Tester(name="tulip_tester_quad", maze = maze, tester_init=(2,2))
    quadruped.set_constraints_opt(constraints_i2)
    quadruped.synthesize_controller()
    quadruped.agent_move((4,0))
    st()
