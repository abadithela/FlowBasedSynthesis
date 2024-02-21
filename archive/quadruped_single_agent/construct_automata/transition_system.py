"""
Script to construct transition system objects of the system and tester.
Apurva Badithela
7/27/23
"""
import sys
sys.path.append("..")
from simulation.maze_network import MazeNetwork
import spot
import pdb
from ast import literal_eval as make_tuple
from buddy import bddtrue
spot.setup()
import matplotlib.pyplot as plt
from itertools import chain, combinations
from collections import OrderedDict as od
import networkx as nx
import os

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

    def get_maze(self, mazefile, int_1, int_2):
        self.maze = MazeNetwork(mazefile)
        self.maze.set_int_1_and_2(int_1, int_2)

    def get_APs(self):
        """
        Set of atomic propositions required to define a specification
        for the maze. Need not initialize all cells of the grid as APs, only
        the relevant states to define what the agent must do.
        Need to setup atomic propositions.
        """
        self.AP = [spot.formula.ap("goal"), spot.formula.ap("int_1"), spot.formula.ap("int_2")]
        self.AP_dict = od()
        for s in self.S: # If the system state is the init or goal
            self.AP_dict[s] = []
            if s == self.maze.goal:
                self.AP_dict[s].append(spot.formula.ap("goal"))
            elif s == self.maze.int_1:
                self.AP_dict[s].append(spot.formula.ap("int_1"))
            elif s == self.maze.int_2:
                self.AP_dict[s].append(spot.formula.ap("int_2"))
        # from ipdb import set_trace as st
        # st()

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

    def construct_labels(self):
        self.L = od()
        for s in self.S:
            if s in self.AP_dict.keys():
                self.L[s] = set(self.AP_dict[s])
            else:
                self.L[s] = {}

    def construct_initial_conditions(self):
        self.I = []
        for s in self.S:
            if s == self.maze.init:
                self.I.append(s)

    def construct_sys(self, mazefile):
        int_1 = (3,4)
        int_2 = (1,0)
        self.get_maze(mazefile, int_1, int_2)
        self.S = list(self.maze.G_single.nodes()) # All system and tester nodes
        self.A = ['sys_n','sys_s','sys_e','sys_w', 'sys_o']
        self.construct_transition_function()
        self.get_APs()
        self.construct_initial_conditions()
        self.construct_labels()
        # self.set_spec()

    # def add_intermediate_nodes(self, node_list):
    #     self.AP.append(spot.formula.ap("int_1")) # Append intermed
    #     for node in node_list:
    #         self.AP_dict[node] = spot.formula.ap("int_2")
    #     self.construct_labels()

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
        # sys_nodes = []
        # tester_nodes = []
        # for n in self.G.nodes():
        #     if n[2] == 's':
        #         sys_nodes.append(n)
        #     else:
        #         tester_nodes.append(n)
        # nx.draw_networkx_nodes(self.G, pos, nodelist=sys_nodes, node_color="yellow")
        # nx.draw_networkx_nodes(self.G, pos, nodelist=tester_nodes, node_color="blue")

        nx.draw_networkx_nodes(self.G, pos, nodelist=self.G.nodes(), node_color="blue")

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
            # if ntuple[2] == "t":
            n.attr['fillcolor'] = 'blue'
            n.attr['shape'] = 'circle'
            # if ntuple[2] == 's':
                # n.attr['fillcolor'] = 'yellow'
                # n.attr['shape'] = 'diamond'
        G_agr.draw(fn+"_dot.pdf",prog='dot')

    def save_plot(self, fn):
        self.to_graph()
        # self.plot_product(fn)
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
