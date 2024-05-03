"""
File to construct synchronous product.
Apurva Badithela
"""
import sys
sys.path.append("..")
import spot
#import buddy
from matplotlib import pyplot as plt
import pdb
from ipdb import set_trace as st
from collections import OrderedDict as od
try:
    from transition_system import ProductTransys, Transys
    from automaton import Automaton
except:
    from components.transition_system import ProductTransys, Transys
    from components.automaton import Automaton
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
        self.G_initial = None
        self.G = None
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

    def instant_pruned_sync_prod(self):
        self.construct_labels()
        self.E = dict()
        aut_state_edges = [(si[0], sj) for si, sj in self.automaton.delta.items()]

        nodes_to_add = []
        s0 = self.transys.I[0]
        q0 = self.automaton.qinit
        nodes_to_add.append((s0, q0))
        nodes_to_keep = []
        nodes_to_keep.append((s0, q0))

        while len(nodes_to_add) > 0:
            next_nodes = []
            for (s,q) in nodes_to_add:
                for a in self.transys.A:
                    if (s,a) in list(self.transys.E.keys()):
                        t = self.transys.E[(s,a)]
                        for p in self.automaton.Q:
                            if (q,p) in aut_state_edges:
                                label = self.transys.L[t]
                                if self.automaton.get_transition(q, label) == p:
                                    self.E[((s,q), a)] = (t,p)
                                    if (t,p) not in nodes_to_keep:
                                        nodes_to_keep.append((t,p))
                                        next_nodes.append((t,p))
            nodes_to_add = next_nodes

        self.S = nodes_to_keep
        self.G_initial = nx.DiGraph()
        nodes = []
        for node in self.S:
            nodes.append(self.Sdict[node])
        self.G_initial.add_nodes_from(nodes)
        edges = []
        for state_act, in_node in self.E.items():
            out_node = state_act[0]
            act = state_act[1]
            s_out = self.Sdict[out_node]
            s_in = self.Sdict[in_node]
            edges.append((s_out, s_in))
        self.G_initial.add_edges_from(edges)
        self.identify_SIT()
        self.to_graph()

    def construct_transitions(self):
        # Debug product
        self.E = dict()
        prod_transys_states = [(si[0], sj) for si, sj in self.transys.E.items()]
        aut_state_pairs = list(product(self.automaton.Q, self.automaton.Q))
        for s,t in prod_transys_states:
            for a in self.transys.A:
                if (s,a) in self.transys.E.keys():
                    for q,p in aut_state_pairs:
                        valid_aut_transition = (self.transys.E[(s,a)] == t)
                        label = self.transys.L[t]
                        valid_sys_transition = (self.automaton.get_transition(q, label) == p)
                        if valid_sys_transition and valid_aut_transition:
                            self.E[((s,q), a)] = (t,p)

    def construct_labels(self):
        self.L = od()
        for s in self.S:
            self.L[s] = s[1]

    def identify_SIT(self):
        self.src = [s for s in self.I]
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


    def plot_graph(self, fn):
        # prune_unreachable_nodes()
        G_agr = self.base_dot_graph(graph=self.G_initial)
        # highlight initial nodes
        state_color_dict = {'red': self.I}
        for color, state_list in state_color_dict.items():
            if not isinstance(state_list, list):
                state_list = [state_list]

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
        G_agr.draw(fn+".pdf",prog='dot')

    def plot_with_highlighted_edges(self, cuts, fn):
        self.identify_SIT()
        self.to_graph()
        # prune unreachable nodes
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
        # highlight initial nodes
        state_color_dict = {'#dc267f': self.I}
        for color, state_list in state_color_dict.items():
            if not isinstance(state_list, list):
                state_list = [state_list]

            for node in state_list:
                if not isinstance(node, str):
                    node_st = self.Sdict[node]
                else:
                    node_st = node

                for i in G_agr.nodes():
                    n = G_agr.get_node(i)
                    if n == node_st:
                        # n.attr['color'] = color
                        n.attr['fillcolor'] = color
                        n.attr['edgecolor'] = 'black'
        # highlight cut edges
        graph_cut_edges = []
        for cut_edge in cuts:
            # st()
            for state_act, in_node in self.E.items():
                out_node = state_act[0]
                # pdb.set_trace()
                if out_node == cut_edge[0] and in_node == cut_edge[1]:
                    graph_cut_edges.append((self.Sdict[out_node], self.Sdict[in_node]))
        for e in G_agr.edges():
            edge = G_agr.get_edge(*e)
            if e in graph_cut_edges:
                e.attr['color'] = 'red'
                e.attr['style'] = 'dashed'
                e.attr['penwidth'] = 2.0
        G_agr.draw(fn+".pdf",prog='dot')

    def prune_unreachable_nodes(self):
        self.identify_SIT()
        self.to_graph()
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
        # G = self.base_dot_graph(graph=self.G_initial)
        # G_agr.draw(fn+"_pruned_unreach_nodes_dot.pdf",prog='dot')

    def base_dot_graph(self, graph=None):
        if graph == None:
            st()
            G_agr = nx.nx_agraph.to_agraph(self.G)
        else:
            G_agr = nx.nx_agraph.to_agraph(graph)

        G_agr.node_attr['style'] = 'filled'
        G_agr.node_attr['gradientangle'] = 90

        for i in G_agr.nodes():
            n = G_agr.get_node(i)
            node = self.reverse_Sdict[n]
            n.attr['shape'] = 'circle'
            if n in self.plt_sink_only:
                n.attr['fillcolor'] = '#ffb000'
            elif n in self.plt_int_only:
                n.attr['fillcolor'] = '#648fff'
            elif n in self.plt_sink_int:
                n.attr['fillcolor'] = '#ffb000'
            elif n in self.plt_src:
                n.attr['fillcolor'] = '#dc267f'
            else:
                n.attr['fillcolor'] = '#ffffff'
            n.attr['label']= ''
        return G_agr

    def plot_product_dot(self, fn):
        # st()
        G_agr = self.base_dot_graph(graph=self.G_initial)
        G_agr.draw(fn+"_dot.pdf",prog='dot')

    def highlight_states(self, state_color_dict, fn):
        G_agr = self.base_dot_graph()
        for color, state_list in state_color_dict.items():
            if not isinstance(state_list, list):
                state_list = [state_list]

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

    def plot_with_highlighted_edges_and_node(self, cuts, fn, highlighted_node):
        print(highlighted_node)
        print(self.Sdict[highlighted_node])
        # st()
        self.identify_SIT()
        self.to_graph()
        # prune unreachable nodes
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
        # highlight special nodes
        state_color_dict = {'#ffffff': s_init, '#fe6100': [highlighted_node]}

        for color, state_list in state_color_dict.items():
            # st()
            if not isinstance(state_list, list):
                state_list = [state_list]

            for node in state_list:
                if not isinstance(node, str):
                    node_st = self.Sdict[node]
                else:
                    node_st = node

                for i in G_agr.nodes():
                    n = G_agr.get_node(i)
                    if n == node_st:
                        # n.attr['color'] = color
                        n.attr['fillcolor'] = color
                        n.attr['edgecolor'] = 'black'
        # highlight cut edges
        graph_cut_edges = []
        for cut_edge in cuts:
            # st()
            for state_act, in_node in self.E.items():
                out_node = state_act[0]
                # pdb.set_trace()
                if out_node == cut_edge[0] and in_node == cut_edge[1]:
                    graph_cut_edges.append((self.Sdict[out_node], self.Sdict[in_node]))
        for e in G_agr.edges():
            edge = G_agr.get_edge(*e)
            if e in graph_cut_edges:
                e.attr['color'] = 'red'
                e.attr['style'] = 'dashed'
                e.attr['penwidth'] = 2.0
        # st()
        G_agr.draw(fn+".pdf",prog='dot')

    def save_plot(self, fn):
        self.identify_SIT()
        self.to_graph()
        self.plot_product_dot(fn)


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


if __name__ == "__main__":
    pdb.set_trace()
