"""
File to construct asynchronous product and synchronous product.
Apurva Badithela
"""
import sys
sys.path.append("..")
import spot
import buddy
from matplotlib import pyplot as plt
import pdb
from collections import OrderedDict as od
from product_transys import ProductTransys, Transys
from automata.example_automata import *
from automata.automata import Automata
import networkx as nx
from itertools import product, chain, combinations
spot.setup(show_default='.tvb')

def powerset(s):
    if type(s)==list:
        s = list(s)
    ps = list(chain.from_iterable(combinations(s, r) for r in range(len(s)+1)))
    return ps

class Product(ProductTransys):
    def __init__(self, product_transys, spec_prod_automaton):
        super().__init__()
        self.transys=product_transys
        self.automaton=spec_prod_automaton
        self.S = list(product(product_transys.S, spec_prod_automaton.Q))
        self.Sdict = od()
        self.reverse_Sdict = od()
        for k in range(len(self.S)):
            self.Sdict[self.S[k]] = "s"+str(k)
            self.reverse_Sdict["s"+str(k)] = self.S[k]
        self.A = product_transys.A
        self.I = [(init, spec_prod_automaton.qinit) for init in product_transys.I]
        self.AP = spec_prod_automaton.Q
    
    def print_transitions(self):
        for e_out, e_in in self.E.items():
            print("node out: " + str(e_out) +  " node in: " + str(e_in))

    def construct_transitions(self):
        # Debug product
        self.E = dict()
        prod_transys_states = [(si[0], sj) for si, sj in self.transys.E.items()]
        aut_state_pairs = list(product(self.automaton.Q, self.automaton.Q))
        for s,t in prod_transys_states:
            #pdb.set_trace()
            for a in self.transys.A:
                if (s,a) in self.transys.E.keys():
                    for q,p in aut_state_pairs:
                        valid_aut_transition = (self.transys.E[(s,a)] == t)
                        label = self.transys.L[t]
                        valid_sys_transition = (self.automaton.get_transition(q, label) == p)
                        if valid_sys_transition and valid_aut_transition:
                            self.E[((s,q), a)] = (t,p)
    
    def construct_transitions_player_labeled(self):
        # Debug product
        self.E = dict()
        prod_transys_states = [(si[0], sj) for si, sj in self.transys.E.items()]
        aut_state_pairs = list(product(self.automaton.Q, self.automaton.Q))
        for s,t in prod_transys_states:
            player = s[2]
            for a in self.transys.A:
                if (s,a) in self.transys.E.keys():
                    for q,p in aut_state_pairs:
                        valid_aut_transition = (self.transys.E[(s,a)] == t)
                        label = self.transys.L[t]
                        valid_sys_transition = (self.automaton.get_player_labeled_transition(q, label, player) == p)
                        if valid_sys_transition and valid_aut_transition:
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

    def plot_product(self, fn):
        pos = nx.kamada_kawai_layout(self.G)
        nx.draw(self.G, pos, node_color="gray")
        
        node_attrs = dict()
        for node, n in self.Sdict.items():
            if node[0][2] == 's':
                node_attrs[n] = {'node_shape': 'diamond'}
            else:
                node_attrs[n] = {'node_shape': 'circle'}
        
        edge_labels = nx.get_edge_attributes(self.G,'act')
        nx.draw_networkx_edges(self.G, pos, edgelist = list(self.G.edges()))
        
        # options = {"edgecolors": "gray", "node_size": 800, "alpha": 0.5}
        options = {"edgecolors": "gray"}
        nx.draw_networkx_nodes(self.G, pos, nodelist=self.plt_sink_only, node_color="yellow", **options)
        nx.draw_networkx_nodes(self.G, pos, nodelist=self.plt_int_only, node_color="blue", **options)
        nx.draw_networkx_nodes(self.G, pos, nodelist=self.plt_sink_int, node_color="green", **options)
        nx.set_node_attributes(self.G, node_attrs)

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
        # G_agr.node_attr['shape'] = 'circle'
        G_agr.node_attr['gradientangle'] = 90

        for i in G_agr.nodes():
            n = G_agr.get_node(i)
            node = self.reverse_Sdict[n]
            if node[0][2] == 's':
                n.attr['shape'] = 'diamond'
            else:
                n.attr['shape'] = 'circle'          
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

def construct_automata_async(AP_set=None):
    Q, qinit, AP, tau, Acc = async_product(state_str="q")
    for ap in AP:
        assert ap in AP_set
    aut = Automata(Q, qinit, AP_set, tau, Acc)
    return aut

def construct_system():
    """
    Construct system from maze.txt
    """
    mazefile = "maze.txt"
    system = ProductTransys()
    system.construct_sys(mazefile)
    return system  

def sync_prod(system, aut):
    sys_prod = Product(system, aut)
    sys_prod.construct_labels()
    sys_prod.construct_transitions()
    return sys_prod  

def async_example():
    system = construct_system()
    aut = construct_automata_async(AP_set = system.AP)
    prod_graph = sync_prod(system, aut)
    prod_graph.save_plot("imgs/prod_graph")

if __name__ == "__main__":
    async_example()
    pdb.set_trace()
    
