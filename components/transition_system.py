"""
Script to construct transition system objects of the system and tester.
Apurva Badithela
7/27/23
"""
import sys
sys.path.append("..")
try:
    from components.maze_network import MazeNetwork
except:
    from maze_network import MazeNetwork
import spot
import pdb
from ast import literal_eval as make_tuple
#from buddy import bddtrue
spot.setup()
import matplotlib.pyplot as plt
from itertools import chain, combinations
from collections import OrderedDict as od
import networkx as nx
import os
from ipdb import set_trace as st

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

    def get_maze(self, mazefile, int, goals, obs):
        self.maze = MazeNetwork(mazefile, obs)
        self.maze.set_int(int)
        self.maze.set_goal(goals)
        self.maze.setup_maze()

    def get_maze_from_network(self, network, inter, goals, obs):
        self.maze = network
        self.maze.set_int(inter)
        self.maze.set_goal(goals)
        self.maze.setup_maze()

    def get_APs(self):
        """
        Set of atomic propositions required to define a specification
        for the maze. Need not initialize all cells of the grid as APs, only
        the relevant states to define what the agent must do.
        Need to setup atomic propositions.
        """
        self.AP = [spot.formula.ap("goal"), spot.formula.ap("int")]
        self.AP_dict = od()
        for s in self.S: # If the system state is the init or goal
            self.AP_dict[s] = []
            if s in self.maze.goal:
                self.AP_dict[s].append(spot.formula.ap("goal"))
            elif s in self.maze.int.keys():
                name_string = self.maze.int[s]
                self.AP_dict[s].append(spot.formula.ap(name_string))

    def print_transitions(self):
        for e_out, e_in in self.E.items():
            print("node out: " + str(e_out) +  " node in: " + str(e_in))

    def construct_transition_function(self):
        self.E = dict()
        for (s, ns) in self.maze.G_single.edges():

            if s[0] == ns[0] + 1 and ns[1] == s[1]:
                self.E[(s, 'sys_s')] = ns
            elif s[0] == ns[0] - 1 and ns[1] == s[1]:
                self.E[(s, 'sys_n')] = ns
            elif ns[0] == s[0] and ns[1] == s[1] + 1:
                self.E[(s, 'sys_e')] = ns
            elif ns[0] == s[0] and ns[1] == s[1] - 1:
                self.E[(s, 'sys_w')] = ns
            elif ns == s:
                self.E[(s, 'sys_o')] = ns
            else:
                print("Incorrect transition function")
                pdb.set_trace()

    def construct_transition_function_fuel(self):
        self.E = dict()
        # st()
        for (s, ns) in self.maze.graph.edges():

            if s[0][0] == ns[0][0] + 1 and ns[0][1] == s[0][1]:
                self.E[(s, 'sys_s')] = ns
            elif s[0][0] == ns[0][0] - 1 and ns[0][1] == s[0][1]:
                self.E[(s, 'sys_n')] = ns
            elif ns[0][0] == s[0][0] and ns[0][1] == s[0][1] + 1:
                self.E[(s, 'sys_e')] = ns
            elif ns[0][0] == s[0][0] and ns[0][1] == s[0][1] - 1:
                self.E[(s, 'sys_w')] = ns
            elif ns == s:
                self.E[(s, 'sys_o')] = ns
            else:
                print("Incorrect transition function")
                pdb.set_trace()

    def construct_transition_function_custom(self):
        # arbitrary actions
        self.E = dict()

        for s in self.maze.states:
            for i, ns in enumerate(self.maze.next_state_dict[s]):
                self.E[(s, self.A[i])] = ns


    def construct_labels(self):
        self.L = od()
        for s in self.S:
            if s in self.AP_dict.keys():
                self.L[s] = set(self.AP_dict[s])
            else:
                self.L[s] = {}

    def construct_initial_conditions(self, init):
        self.I = init
        self.maze.init = self.I


    def construct_sys(self, mazefile, init, ints, goals, obs=[]):
        self.get_maze(mazefile, ints, goals, obs)
        self.S = list(self.maze.G_single.nodes())
        self.A = ['sys_n','sys_s','sys_e','sys_w', 'sys_o']
        self.construct_transition_function()
        self.get_APs()
        self.construct_initial_conditions(init)
        self.construct_labels()

    def construct_sys_from_network(self, network, init, ints, goals, obs=[]):
        self.get_maze_from_network(network, ints, goals, obs)
        self.S = list(self.maze.graph.nodes())
        self.A = ['sys_n','sys_s','sys_e','sys_w', 'sys_o']
        self.construct_transition_function_fuel()
        self.get_APs()
        self.construct_initial_conditions(init)
        self.construct_labels()

    def construct_sys_from_custom_network(self, custom_network, init, ints, goals, obs=[]):
        self.get_maze_from_network(custom_network, ints, goals, obs)
        self.S = list(self.maze.G.nodes())
        self.A = ['a','b','c','d', 'e'] # placeholders, don't care
        self.construct_transition_function_custom()
        # st()
        self.get_APs()
        self.construct_initial_conditions(init)
        self.construct_labels()
        # st()

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


    def plot_product_dot(self, fn):
        G_agr = nx.nx_agraph.to_agraph(self.G)
        G_agr.node_attr['style'] = 'filled'
        G_agr.node_attr['gradientangle'] = 90

        for i in G_agr.nodes():
            n = G_agr.get_node(i)
            ntuple = make_tuple(n)
            n.attr['fillcolor'] = 'blue'
            n.attr['shape'] = 'circle'

        G_agr.draw(fn+"_dot.pdf",prog='dot')

    def save_plot(self, fn):
        self.to_graph()
        self.plot_product_dot(fn)

def powerset(s):
    if type(s)==list:
        s = list(s)
    ps = list(chain.from_iterable(combinations(s, r) for r in range(len(s)+1)))
    return ps

if __name__ == "__main__":
    cur_path = os.path.dirname(__file__)
    mazefile = os.path.relpath('../simulation/maze.txt', cur_path)
    product = ProductTransys()
    product.construct_sys(mazefile)
    # product.print_transitions()

    product.save_plot("imgs/product_transys")
    pdb.set_trace()
