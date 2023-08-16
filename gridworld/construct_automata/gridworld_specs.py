"""
File to instantiate gridworld, construct atomic propositions and formulas
Apurva Badithela
6/26/23
"""

import sys
sys.path.append("../simulations/")
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
        for s in self.maze.states:
            if s in self.AP_dict.keys():
                self.L[s] = {self.AP_dict[s]}
            else:
                self.L[s] = {}
        
    
    def construct_sys(self, mazefile):
        self.get_maze(mazefile)
        self.get_APs()
        self.S = self.maze.states
        self.A = ['n','s','e','w', 'o']
        self.construct_transition_function()
        self.I = self.maze.source
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
    mazefile = "../gridworld/maze.txt"
    system = System()
    system.construct_sys(mazefile)
    pdb.set_trace()
