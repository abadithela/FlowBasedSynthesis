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
        self.cuts = [(GD.inv_node_dict[u], GD.inv_node_dict[v]) for (u,v) in annot_cuts]
        # self.cuts = [(34, 50), (44, 28)]
        self.cuts_to_blocked_edges()
        self.get_map_G_to_S()
        self.cuts_to_blocked_states()
        self.map_system_state_to_blocked_states()
        
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

    def cuts_to_blocked_edges(self):
        for edge_cut in self.cuts:
            u, v = edge_cut
            u_st = self.GD.node_dict[u]
            v_st = self.GD.node_dict[v]
            self.blocked_edges.append((u_st, v_st))
        
    def map_system_state_to_blocked_states(self):
        '''
        When a state is blocked by the tester, we also need information of
        the corresponding system state. For instance, if (u,v) is the edge that is cut,
        and u is the blocked state occupied by the tester, then all predecessors of u are 
        possible states of the system that are constrained.
        '''
        self.cuts_with_dynamic_agent = []
        for blocked_st in self.blocked_states:
            node_k = self.GD.inv_node_dict[blocked_st]
            for predecessor in self.GD.graph.predecessors(node_k):
                predecessor_st = self.GD.node_dict[predecessor]
                self.cuts_with_dynamic_agent.append((predecessor_st, blocked_st))


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
