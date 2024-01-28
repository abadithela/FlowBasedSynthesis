# File to parse optimization constraints from the output of the optimization
import sys
sys.path.append('../..')
import numpy as np
from ipdb import set_trace as st
import networkx as nx
from find_cuts import find_cuts
from optimization.feasibility_constraints import find_map_G_S
# from synthesize_tester_from_constraints import Quadruped_Tester
from components.maze_network import MazeNetwork

class MapConstraints:
    def __init__(self, annot_cuts, GD, SD):
        self.blocked_edges = []
        self.blocked_states = []
        self.annot_cuts = annot_cuts
        self.GD = GD
        self.SD = SD
        self.cuts = [(34, 50), (44, 28)]
        self.cuts_to_blocked_edges()
        self.get_map_G_to_S()
        self.cuts_to_blocked_states()
        
    def get_virtual_product_graph(self):
        return self.GD

    def get_system_product_graph(self):
        return self.SD

    def get_map_G_to_S(self):
        self.map_G_to_S = find_map_G_S(self.GD, self.SD)

    def get_blocked_states(self):
        return self.blocked_states

    def get_blocked_edges(self):
        return self.blocked_edges

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

    def cuts_to_blocked_edges(self):
        for edge_cut in self.cuts:
            u, v = edge_cut
            u_st = self.GD.node_dict[u]
            v_st = self.GD.node_dict[v]
            self.blocked_edges.append((u_st, v_st))
        st()

    def map_system_state_to_blocked_states(self):
        '''
        When a state is blocked by the tester, we also need information of
        the corresponding system state
        TO-DO: Finish implementing.
        '''
        self.constraint_map = dict()
        for blocked_st in self.blocked_states:
            tester_st = blocked_st[0]
            self.constraint_map[tester_st] = None

    def cuts_to_blocked_states(self):
        self.blocked_states = []
        for edge_cut in self.cuts:
            u, v = edge_cut
            exist_path_u = self.check_path_in_S(u)
            exist_path_v = self.check_path_in_S(v)
            if exist_path_u:
                u_st = self.GD.node_dict[u]
                self.blocked_states.append(u_st)
            elif exist_path_v:
                v_st = self.GD.node_dict[v]
                self.blocked_states.append(v_st)
            else:
                print("Cannot place static obstacle. Must constrain edge instead")
                st()

    def parse_cuts_to_states(self):
        self.cuts_to_blocked_states()
        # With reactive obstacles, implement code here to convert blocked states to system and tester states. This
        # would require reasoning over Bpi.
        constraints_i1 = [((4,1),(3,2)), ((4,2),(3,2)), ((4,3),(3,2)), ((4,4), (3,2)), ((2,2),(1,2))]
        constraints_i2 = [((4,2),(3,2)), ((2,2),(1,2))]
        constraints = [((4,2),(3,2), "q0"), ((2,2),(1,2), "q3")]
        return constraints

if __name__ == "__main__":
    mazefile = 'maze.txt'
    maze = MazeNetwork(mazefile)
    opt_constr = MapConstraints()
    constraints = opt_constr.parse_cuts_to_states()
    blocked_states = opt_constr.get_blocked_states()
    blocked_edges= opt_constr.get_blocked_edges()
    # quadruped = Quadruped_Tester(name="tulip_tester_quad", maze = maze, tester_init=(4,2))
    # quadruped.set_constraints_opt(constraints)
    # quadruped.synthesize_controller()
    # quadruped.agent_move((4,0))
    st()
