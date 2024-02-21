"""
This file plots graphs by clustering them to avoid graph explosion.
"""

import networkx as nx
from products import *
from matplotlib import pyplot as plt

class GraphPlot:
    def __init__(self, prod_graph, sys, aut):
        self.prod_graph = prod_graph # Full product graph
        self.identify_src_int_target()
        self.sys = sys
        self.aut = aut
        self.graph = nx.DiGraph() # Abstracted graph
        self.clusters = dict() # Mapping cluster label to explicit states in the product graph; a node cannot belong to multiple clusters
        self.cluster_names = dict() # Mapping cluster label to a description of the set of states
        self.node_cluster_name = dict() # Dictionary mapping a node to its cluster name
        self.cluster_plot_options = dict()
        
    
    def identify_src_int_target(self):
        self.prod_graph.identify_SIT()
        self.prod_graph.to_graph()
        for state_act, in_node in self.prod_graph.E.items():
            out_node = state_act[0]
            self.prod_graph.process_nodes([out_node, in_node])

    def set_cluster_names(self):
        for q in self.aut.Q:
            self.cluster_names.update({q:[]})
        self.cluster_names.update({"src":[]})
        self.cluster_names.update({"int":[]}) # intermediate_only
        self.cluster_names.update({"sink":[]}) # sink only
        self.cluster_names.update({"int_and_sink":[]}) # int and sink
        for node, node_st in self.prod_graph.Sdict.items():
            self.node_cluster_name[node_st] = None

    def check_parents_aut_states(self, node, parents):
        cluster_name = None
        parents_q = [p[1] for p in parents]
        if node[1] in parents_q: 
            indices = [i for i,x in enumerate(parents_q) if x==node[1]]
            parent_cluster_names = []
            for i in indices:
                parenti_cluster_name = self.node_cluster_name[parents[i]]
                if parenti_cluster_name is not None and parenti_cluster_name not in parent_cluster_names:
                    parent_cluster_names.append(parenti_cluster_name)
                    if len(parent_cluster_names)>1:
                        print("Multiple cluster names possible")
            cluster_name = parent_cluster_names[0]
        return cluster_name

    def check_parents_SIT_states(self, node, parents):
        cluster_name = None
        parents_q = [p[1] for p in parents]
        if node[1] in parents_q: 
            indices = [i for i,x in enumerate(parents_q) if x==node[1]]
            parent_cluster_names = []
            for i in indices:
                parenti_cluster_name = self.node_cluster_name[parents[i]]
                if parenti_cluster_name is not None and parenti_cluster_name not in parent_cluster_names:
                    parent_cluster_names.append(parenti_cluster_name)
                    if len(parent_cluster_names)>1:
                        print("Multiple cluster names possible")
            cluster_name = parent_cluster_names[0]
        return cluster_name

    def check_parents_cluster(self, node):
        node_st = self.prod_graph.Sdict[node]
        parents_st = self.prod_graph.G.predecessors(node_st)
        parents = [self.prod_graph.reverse_Sdict[p] for p in parents_st]
        cluster_name_aut = self.check_parents_aut_states(node, parents)
        cluster_name_SIT = self.check_parents_SIT_states(node, parents)

    def cluster_nodes(self):
        """
        Clustering nodes according to the states of the automaton and strongly connected components
        """
        edges = []
        edge_attr = dict()
        node_attr = dict()
        already_clustered = []
        self.set_cluster_names()
        for node in self.prod_graph.S:
            self.check_parents_cluster(node)
            self.cluster_names.update({node[1]: self.prod_graph.Sdict[node]})
            pdb.set_trace()
        
        self.graph.add_edges_from(edges)
        nx.set_edge_attributes(self.graph, edge_attr)
        
    def cluster_scc(self):
        self.prod_scc = list(nx.strongly_connected_components(self.prod_graph.G))
    
    def refine_cluster(self, condition):
        """
        Refine the clusters in the graph according to the condition 
        """
        # check clusters for condition
        # update the clusters and cluster_names
        # replot graph according to the condition
        # 
        pass
    
    def nx_plot_graph(self):
        """
        Plotting the current self.graph with networkx
        """
        pos = nx.kamada_kawai_layout(self.graph)
        nx.draw_networkx_edges(self.graph, pos, edgelist = list(self.graph.edges()))
        
        for cluster_name, cluster in self.cluster.items():
            options = self.cluster_plot_options[cluster_name]
            nx.draw_networkx_nodes(self.graph, pos, nodelist=[cluster_name], **options)

        plt.tight_layout()
        plt.axis("off")
        plt.savefig("nx_cluster_plot.png")
        plt.show()

    def dot_plot_graph(self):
        """
        Plotting the current self.graphraph with pydot
        """
        G_agr = nx.nx_agraph.to_agraph(self.graph)

        G_agr.node_attr['style'] = 'filled'
        G_agr.node_attr['shape'] = 'circle'
        G_agr.node_attr['gradientangle'] = 90

        for cluster_name, cluster in self.cluster.items():
            options = self.cluster_plot_options[cluster_name]
            for attr, attr_val in options:
                cluster_name.attr[attr] = attr_name
        G_agr.draw("cluster_plot_dot.png",prog='dot')

    def parse_cut(self, cut_edge):
        graph_cut_edges = []
        for state_act, in_node in self.prod_graph.E.items():
            out_node = state_act[0]
            # pdb.set_trace()
            if out_node[0] == cut_edge[0] and in_node[0] == cut_edge[1]:
                graph_cut_edges.append((self.prod_graph.Sdict[out_node], self.prod_graph.Sdict[in_node]))
        return graph_cut_edges

    def get_base_graph(self):
        G_agr = nx.nx_agraph.to_agraph(self.prod_graph.G)
        G_agr.node_attr['style'] = 'filled'
        G_agr.node_attr['shape'] = 'circle'
        G_agr.node_attr['gradientangle'] = 90

        for i in G_agr.nodes():
            n = G_agr.get_node(i)
            if n in self.prod_graph.plt_sink_only:
                n.attr['fillcolor'] = 'yellow'
            elif n in self.prod_graph.plt_int_only:
                n.attr['fillcolor'] = 'blue'
            elif n in self.prod_graph.plt_sink_int:
                n.attr['fillcolor'] = 'blue;0.5:yellow'
            elif n in self.prod_graph.plt_src:
                n.attr['fillcolor'] = 'magenta'
            else:
                n.attr['fillcolor'] = 'gray'
        return G_agr

    def plot_cut_prod_graph(self, cut_edge):
        """
        Plot cut edges specified in list cut_edges on the abstract graph. If the cuts are within a cluster, 
        we would have to refine the cluster to view the cuts.
        """
        graph_cut_edges = self.parse_cut(cut_edge)
        G_agr = self.get_base_graph()
        for e in G_agr.edges():
            edge = G_agr.get_edge(*e)
            if e in graph_cut_edges:
                e.attr['color'] = 'red'
                e.attr['style'] = 'dashed'
                e.attr['penwidth'] = 2.0
        G_agr.draw("imgs/graph_cuts_dot.png",prog='dot')
    
