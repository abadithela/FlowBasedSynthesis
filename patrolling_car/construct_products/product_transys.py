"""
Script to construct transition system objects of the system and tester.
Apurva Badithela
7/27/23
"""
import sys
sys.path.append("..")
from graph.maze_network import MazeNetwork
import spot
import pdb
from ast import literal_eval as make_tuple
from buddy import bddtrue
spot.setup()
import matplotlib.pyplot as plt
from itertools import chain, combinations
from collections import OrderedDict as od
import networkx as nx

class Transys():
    def __init__(self, S=None, A=None, E=None, I=None, AP=None, L=None):
        self.S = S
        self.A = A
        self.E = E
        self.I = I
        self.AP = AP
        self.L = L
    
class ProductTransys(Transys):
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
        Need to setup atomic propositions.
        """
        self.AP = [spot.formula.ap("home"), spot.formula.ap("park"), spot.formula.ap("refuel")]
        # self.AP.append(spot.formula.ap("src"))
        self.AP_dict = od() 
        for s in self.S: # If the system state is the init or goal
            self.AP_dict[s] = []
            if s[0] == self.maze.init and s[1] == self.maze.tester_init:
                self.AP_dict[s].append(spot.formula.ap("src"))
            elif s[0] == self.maze.goal:
                self.AP_dict[s].append(self.AP[0])
            elif s[0] == self.maze.park:
                self.AP_dict[s].append(self.AP[1])
            elif s[0] == self.maze.refuel:
                self.AP_dict[s].append(self.AP[2])
            
            # if s[-1] == "empty":
            #     self.AP_dict[s].append(spot.formula.ap("empty"))
            # else:
            #     self.AP_dict[s].append(spot.formula.Not(spot.formula.ap("empty")))

    # Add plotting feature
    def define_spec(self):
        fstr = "F(sink)"
        return fstr
    
    def print_transitions(self):
        for e_out, e_in in self.E.items():
            print("node out: " + str(e_out) +  " node in: " + str(e_in))
        
    def set_spec(self):
        fstr = self.define_spec()
        self.f = spot.formula(fstr)
    
    def construct_transition_function(self):
        self.E = dict()
        for (s, ns) in self.maze.G.edges():
            s_sys, s_test, s_player = self.maze.player(s)
            ns_sys, ns_test, ns_player = self.maze.player(ns)
            if s_player == "s":
                assert ns_player == "t"
                action = "sys_"
                state_curr = s_sys
                state_next = ns_sys
            else:
                assert ns_player == "s"
                action = "test_"
                state_curr = s_test
                state_next = ns_test
            
            if state_next[0]==state_curr[0] + 1 and state_next[1]==state_curr[1]:
                self.E[(s, action+'s')] = ns
            elif state_next[0]==state_curr[0] - 1 and state_next[1]==state_curr[1]:
                self.E[(s, action+'n')] = ns
            elif state_next[0]==state_curr[0] and state_next[1]==state_curr[1] + 1:
                self.E[(s, action+'e')] = ns
            elif state_next[0]==state_curr[0] and state_next[1]==state_curr[1] - 1:
                self.E[(s, action+'w')] = ns
            elif state_next==state_curr:
                self.E[(s, action+'o')] = ns
            else:
                print("Incorrect transition function")
                pdb.set_trace()
            # if (s,'o') not in self.E.keys(): # System can wait
            #     self.E[(s,'o')] = s

    def construct_labels(self):
        self.L = od()
        for s in self.S:
            if s in self.AP_dict.keys():
                self.L[s] = set(self.AP_dict[s])
            else:
                self.L[s] = {}
    
    def construct_initial_conds(self):
        self.I = []
        for s in self.S:
            if s[0] == self.maze.init and s[1] == self.maze.tester_init:
                self.I.append(s)

    def construct_sys(self, mazefile):
        self.get_maze(mazefile)
        self.S = list(self.maze.G.nodes()) # All system and tester nodes
        self.A = ['sys_n','sys_s','sys_e','sys_w', 'sys_o', 'test_n','test_s','test_e','test_w', 'test_o']
        self.construct_transition_function()
        self.get_APs()
        self.construct_initial_conds()
        self.construct_labels()
        self.set_spec()

    def add_intermediate_nodes(self, node_list):
        self.AP.append(spot.formula.ap("int")) # Append intermed
        for node in node_list:
            self.AP_dict[node] = spot.formula.ap("int")
        self.construct_labels()
    
    def add_set_intermediate_nodes(self, node_dict):
        for node, formula in node_dict.items():
            if formula not in self.AP:
                self.AP.append(formula) # Append intermed
            self.AP_dict[node] = formula
        self.construct_labels()

    def to_graph(self):
        self.G = nx.DiGraph()
        self.G.add_nodes_from(list(self.S))
        
        edges = []
        edge_attr = dict()
        node_attr = dict()
        for state_act, in_node in self.E.items():
            out_node = state_act[0]
            act = state_act[1]
            edge = (out_node, in_node)
            edge_attr[edge] = {"act": act}
            edges.append(edge)
            # pdb.set_trace()
        self.G.add_edges_from(edges)
        nx.set_edge_attributes(self.G, edge_attr)

    def plot_product(self, fn):
        pos = nx.kamada_kawai_layout(self.G)
        sys_nodes = []
        tester_nodes = []
        for n in self.G.nodes():
            if n[2] == 's':
                sys_nodes.append(n)
            else:
                tester_nodes.append(n)
        nx.draw_networkx_nodes(self.G, pos, nodelist=sys_nodes, node_color="yellow")
        nx.draw_networkx_nodes(self.G, pos, nodelist=tester_nodes, node_color="blue")
        # node_labels = nx.get_node_attributes(G,'state')
        # nx.draw_networkx_labels(G, pos, labels = node_labels)
        edge_labels = nx.get_edge_attributes(self.G,'act')
        nx.draw_networkx_edges(self.G, pos, edgelist = list(self.G.edges()))
        
        options = {"edgecolors": "tab:gray", "node_size": 800, "alpha": 0.5}

        plt.tight_layout()
        plt.axis("off")
        plt.savefig(fn+".pdf")
        # plt.show()

    def plot_product_dot(self, fn):
        G_agr = nx.nx_agraph.to_agraph(self.G)
        G_agr.node_attr['style'] = 'filled'
        G_agr.node_attr['gradientangle'] = 90

        for i in G_agr.nodes():
            n = G_agr.get_node(i)
            ntuple = make_tuple(n)
            if ntuple[2] == "t":
                n.attr['fillcolor'] = 'blue'
                n.attr['shape'] = 'circle'
            if ntuple[2] == 's':
                n.attr['fillcolor'] = 'yellow'
                n.attr['shape'] = 'diamond'
        G_agr.draw(fn+"_dot.pdf",prog='dot')

    def save_plot(self, fn):
        self.to_graph()
        self.plot_product(fn)
        self.plot_product_dot(fn)

def powerset(s):
    if type(s)==list:
        s = list(s)
    ps = list(chain.from_iterable(combinations(s, r) for r in range(len(s)+1)))
    return ps

if __name__ == "__main__":
    mazefile = "maze.txt"
    product = ProductTransys()
    product.construct_sys(mazefile)
    # product.print_transitions()
    product.save_plot("imgs/product_transys")
    pdb.set_trace()