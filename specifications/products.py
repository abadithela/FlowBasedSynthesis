"""
File to construct asynchronous product and synchronous product.
"""
import sys
import spot
from spot.jupyter import display_inline
import buddy
from matplotlib import pyplot as plt
import pdb
from collections import OrderedDict as od
from gridworld_specs import TranSys, System
from example_automata import *
from automata import Automata
import networkx as nx
from itertools import product, chain, combinations
spot.setup(show_default='.tvb')

def powerset(s):
    if type(s)==list:
        s = list(s)
    ps = list(chain.from_iterable(combinations(s, r) for r in range(len(s)+1)))
    return ps

class Product(TranSys):
    def __init__(self, system, automaton):
        super().__init__()
        self.system=system
        self.automaton=automaton
        self.S = list(product(system.S, automaton.Q))
        self.Sdict = od()
        for k in range(len(self.S)):
            self.Sdict[self.S[k]] = "s"+str(k)
        self.A = system.A
        self.I = (system.I, automaton.qinit)
        self.AP = automaton.Q
    
    def construct_transitions(self):
        self.E = dict()
        sys_state_pairs = list(product(self.system.S, self.system.S))
        aut_state_pairs = list(product(self.automaton.Q, self.automaton.Q))
        for s,t in sys_state_pairs:
            for a in self.system.A:
                if (s,a) in self.system.E.keys():
                    for q,p in aut_state_pairs:
                        valid_aut_transition = (self.system.E[(s,a)] == t)
                        label = self.system.L[t]
                        valid_sys_transition = (self.automaton.get_transition(q, label) == p)
                        if valid_sys_transition and valid_aut_transition:
                            # pdb.set_trace()
                            self.E[((s,q), a)] = (t,p)

    def construct_labels(self):
        self.L = od()
        for s in self.S:
            self.L[s] = s[1]
    
    def identify_SIT(self):
        self.src = [s for s in self.S if s[1] == self.automaton.qinit]
        try:
            self.int = [s for s in self.S if s[1] in self.automaton.Acc["test"]]
        except:
            self.int=[]
        self.sink = [s for s in self.S if s[1] in self.automaton.Acc["sys"]]
    
    def process_nodes(self, node_list):
        for node in node_list:
            node_st = self.Sdict[node]
            if node in self.sink and node not in self.int:
                if node_st not in self.plt_sink_only:
                    self.plt_sink_only.append(node_st)
            
            if node in self.int and node not in self.sink:
                if node_st not in self.plt_int_only:
                    self.plt_int_only.append(node_st)
            
            if node in self.int and node in self.sink:
                if node_st not in self.plt_sink_int:
                    self.plt_sink_int.append(node_st)

    def to_graph(self):
        self.G = nx.DiGraph()
        self.G.add_nodes_from(list(self.Sdict.values()))
        self.plt_sink_only = [] # Finding relevant nodes connected to graph with edges
        self.plt_int_only= []
        self.plt_sink_int = []
        edges = []
        edge_attr = dict()
        node_attr = dict()
        for state_act, in_node in self.E.items():
            out_node = state_act[0]
            act = state_act[1]
            edge = (self.Sdict[out_node], self.Sdict[in_node])
            edge_attr[edge] = {"act": act}
            edges.append(edge)
            self.process_nodes([out_node, in_node])
        self.G.add_edges_from(edges)
        nx.set_edge_attributes(self.G, edge_attr)

        # for node_tuple, node in self.Sdict.items():
        #     if node_tuple in self.sink:
        #         node_attr[node] = {"Acc": "T"}

    def plot_product(self, fn):
        pos = nx.kamada_kawai_layout(self.G)
        nx.draw(self.G, pos, node_color="gray")
        # node_labels = nx.get_node_attributes(G,'state')
        # nx.draw_networkx_labels(G, pos, labels = node_labels)
        edge_labels = nx.get_edge_attributes(self.G,'act')
        nx.draw_networkx_edges(self.G, pos, edgelist = list(self.G.edges()))
        
        options = {"edgecolors": "tab:gray", "node_size": 800, "alpha": 0.5}
        nx.draw_networkx_nodes(self.G, pos, nodelist=self.plt_sink_only, node_color="tab:red", **options)
        nx.draw_networkx_nodes(self.G, pos, nodelist=self.plt_int_only, node_color="tab:blue", **options)
        nx.draw_networkx_nodes(self.G, pos, nodelist=self.plt_sink_int, node_color="tab:purple", **options)

        plt.tight_layout()
        plt.axis("off")
        plt.savefig(fn+".png")
        # plt.show()

    def plot_product_dot(self, fn):
        G_agr = nx.nx_agraph.to_agraph(self.G)

        G_agr.node_attr['style'] = 'filled'
        G_agr.node_attr['shape'] = 'circle'
        G_agr.node_attr['gradientangle'] = 90

        for i in G_agr.nodes():
            n = G_agr.get_node(i)
            if n in self.plt_sink_only:
                n.attr['fillcolor'] = 'yellow'
            elif n in self.plt_int_only:
                n.attr['fillcolor'] = 'blue'
            elif n in self.plt_sink_int:
                n.attr['fillcolor'] = 'blue;0.5:yellow'
            else:
                n.attr['fillcolor'] = 'gray'

        G_agr.draw(fn+"_dot.png",prog='dot')


    def save_plot(self, fn):
        self.identify_SIT()
        self.to_graph()
        self.plot_product(fn)
        self.plot_product_dot(fn)

    def list_edges(self):
        for e, in_e in self.E.items():
            print(e," : ", in_e)
        
def construct_automata_simple(AP_set=None):
    Q, qinit, AP, tau, Acc = eventually(state_str="q", formula="sink")
    for ap in AP:
        assert ap in AP_set
    aut = Automata(Q, qinit, AP_set, tau, Acc)
    return aut

def construct_automata_async(AP_set=None):
    Q, qinit, AP, tau, Acc, Qdict = async_eventually(state_str="q")
    for ap in AP:
        assert ap in AP_set
    aut = Automata(Q, qinit, AP_set, tau, Acc)
    return aut

def construct_system():
    mazefile = "../gridworld/maze.txt"
    system = System()
    system.construct_sys(mazefile)
    int_node_list = [(2,2)]
    system.add_intermediate_nodes(int_node_list)
    return system

def construct_quadruped_system():
    mazefile = "../gridworld/quadruped_maze.txt"
    system = System()
    system.construct_sys(mazefile)
    int_node_list = od()
    int_node_list[(3,4)] = spot.formula.ap("int1")
    int_node_list[(1,0)] = spot.formula.ap("int2")
    system.add_set_intermediate_nodes(int_node_list)
    return system

def construct_quadruped_automata(AP_set=None):
    Q, qinit, AP, tau, Acc = quadruped_maze(state_str="q")
    for ap in AP:
        assert ap in AP_set
    aut = Automata(Q, qinit, AP_set, tau, Acc)
    return aut

def sync_prod(system, aut):
    sys_prod = Product(system, aut)
    sys_prod.construct_labels()
    sys_prod.construct_transitions()
    return sys_prod    

def simple_example():
    system = construct_system()
    aut = construct_automata_simple(AP_set = system.AP) # ensure that all system atomic propositions are maintained
    sys_prod = sync_prod(system, aut)
    sys_prod.save_plot("imgs/maze_sys_prod.png")

def async_example():
    system = construct_system()
    aut = construct_automata_async(AP_set = system.AP)
    prod_graph = sync_prod(system, aut)
    prod_graph.save_plot("imgs/prod_graph")

def quadruped_example():
    # Needs to be fixed!!!!
    system = construct_quadruped_system()
    # pdb.set_trace()
    aut = construct_quadruped_automata(AP_set = system.AP)
    prod_graph = sync_prod(system, aut)
    prod_graph.save_plot("imgs/quadruped_prod_graph")

if __name__ == "__main__":
    # If simple system:
    # system = construct_system()
    # aut = construct_automata_simple(AP_set = system.AP) # ensure that all system atomic propositions are maintained
    # sys_prod = sync_prod(system, aut)
    # pdb.set_trace()
    # sys_prod.save_plot("imgs/maze_sys_prod.png")

    # If async product and simple system:
    # system = construct_system()
    # aut = construct_automata_async(AP_set = system.AP)
    # prod_graph = sync_prod(system, aut)
    # prod_graph.save_plot("imgs/prod_graph")
    
    # simple_example()
    quadruped_example()
    pdb.set_trace()
    
