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
from product_automata_gridworld import *
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
        self.reverse_Sdict = od()
        for k in range(len(self.S)):
            self.Sdict[self.S[k]] = "s"+str(k)
            self.reverse_Sdict["s"+str(k)] = self.S[k]
        self.A = system.A
        self.I = (system.I, automaton.qinit)
        self.AP = automaton.Q
    
    def get_aut_state(self, product_s):
        '''
        Retrieving automata state from product state
        '''
        return product_s[1]
    
    def get_sys_state(self, product_s):
        '''
        Retrieving system state from product state
        '''
        return product_s[0]
    
    def get_action_from_edge(self, state_act, in_node):
        '''
        Retrieve action causing the transition
        '''
        edge = (state_act, in_node)
        assert edge in self.E
        return state_act[1]

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

    def prune_unreachable_nodes(self, fn):
        self.G_initial = nx.DiGraph()
        s_init = [self.Sdict[i] for i in self.I]
        init_dfs_tree = [nx.dfs_tree(self.G, source=src) for src in s_init]
        init_dfs_tree_nodes = []
        for tree in init_dfs_tree:
            for n in tree.nodes():
                if n not in init_dfs_tree_nodes:
                    init_dfs_tree_nodes.append(n)
        edges = []
        for state_act, in_node in self.E.items():
            out_node = state_act[0]
            act = state_act[1]
            s_out = self.Sdict[out_node]
            s_in = self.Sdict[in_node]
            edge = (s_out, s_in)
            if s_out in init_dfs_tree_nodes:
                edges.append(edge)
        self.G_initial.add_edges_from(edges)
        G_agr = self.base_dot_graph(graph=self.G_initial)
        G_agr.draw(fn+"_pruned_unreach_nodes_dot.pdf",prog='dot')

    def highlight_states(self, state_color_dict, fn):
        G_agr = self.base_dot_graph()
        for color, state_list in state_color_dict.items():
            if not isinstance(state_list, list):
                state_list = [state_list]
            # pdb.set_trace()
            
            for node in state_list:
                if not isinstance(node, str):
                    node_st = self.Sdict[node]
                else:
                    node_st = node

                for i in G_agr.nodes():
                    n = G_agr.get_node(i)
                    if n == node_st:
                        n.attr['color'] = color
                        n.attr['fillcolor'] = color
        G_agr.draw(fn+"_highlight_dot.pdf",prog='dot')

    def construct_labels(self):
        self.L = od()
        for s in self.S:
            self.L[s] = s[1]
    
    def identify_SIT(self):
        self.src = [s for s in self.S if s == self.I]
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
            
            if node in self.src:
                if node_st not in self.plt_src:
                    self.plt_src.append(node_st)

    def to_graph(self):
        self.G = nx.DiGraph()
        self.G.add_nodes_from(list(self.Sdict.values()))
        self.plt_sink_only = [] # Finding relevant nodes connected to graph with edges
        self.plt_int_only= []
        self.plt_sink_int = []
        self.plt_src = []
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

    def plot_product(self, fn):
        pos = nx.kamada_kawai_layout(self.G)
        nx.draw(self.G, pos, node_color="gray")
                
        edge_labels = nx.get_edge_attributes(self.G,'act')
        nx.draw_networkx_edges(self.G, pos, edgelist = list(self.G.edges()))
        
        options = {"edgecolors": "tab:gray", "node_size": 800, "alpha": 0.5}
        nx.draw_networkx_nodes(self.G, pos, nodelist=self.plt_sink_only, node_color="tab:red", **options)
        nx.draw_networkx_nodes(self.G, pos, nodelist=self.plt_int_only, node_color="tab:blue", **options)
        nx.draw_networkx_nodes(self.G, pos, nodelist=self.plt_sink_int, node_color="tab:purple", **options)
        plt.tight_layout()
        plt.axis("off")
        plt.savefig(fn+".pdf")
        # plt.show()

    def base_dot_graph(self, graph=None):
        if graph == None:
            G_agr = nx.nx_agraph.to_agraph(self.G)
        else:
            G_agr = nx.nx_agraph.to_agraph(graph)

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
        return G_agr

    def plot_product_dot(self, fn):
        G_agr = self.base_dot_graph()
        G_agr.draw(fn+"_dot.pdf",prog='dot')

    def parse_cut(self, cut_edge):
        graph_cut_edges = []
        for state_act, in_node in self.E.items():
            out_node = state_act[0]
            # pdb.set_trace()
            if out_node[0] == cut_edge[0] and in_node[0] == cut_edge[1]:
                graph_cut_edges.append((self.Sdict[out_node], self.Sdict[in_node]))
        return graph_cut_edges

    def plot_cut_prod_graph(self, cut_edge, fn):
        """
        Plot cut edges specified in list cut_edges on the abstract graph. If the cuts are within a cluster, 
        we would have to refine the cluster to view the cuts.
        """
        graph_cut_edges = self.parse_cut(cut_edge)
        G_agr = self.base_dot_graph()
        for e in G_agr.edges():
            edge = G_agr.get_edge(*e)
            if e in graph_cut_edges:
                e.attr['color'] = 'red'
                e.attr['style'] = 'dashed'
                e.attr['penwidth'] = 2.0
        G_agr.draw(fn+"_dot.pdf",prog='dot')

    def save_plot(self, fn):
        self.identify_SIT()
        self.to_graph()
        self.plot_product(fn)
        self.plot_product_dot(fn)

    def print_neighbors(self, node):
        if not isinstance(node, str):
            node_st = self.Sdict[node]
        else:
            node_st = node
        predecessors = self.G.predecessors(node_st)
        successors = self.G.successors(node_st)
        print("List of predecessor nodes: ")
        for p in predecessors:
            print(p)
        print("\n")
        print("List of successor nodes: ")
        for p in successors:
            print(p)

    def list_edges(self):
        for e, in_e in self.E.items():
            print(e," : ", in_e)

    def list_nodes(self):
        for n, n_st in self.Sdict.items():
            print(n, " : ", n_st)

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

def construct_automata_sync(AP_set=None):
    Q, qinit, AP, tau, Acc, Qdict = sync_eventually(state_str="q")
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
    # prod_graph.save_plot("imgs/prod_graph")
    return system, aut, prod_graph

def sync_example():
    system = construct_system()
    aut = construct_automata_sync(AP_set = system.AP)
    prod_graph = sync_prod(system, aut)
    # prod_graph.save_plot("imgs/prod_graph")
    return system, aut, prod_graph


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
    
