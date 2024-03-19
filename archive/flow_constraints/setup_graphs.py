import networkx as nx
from ipdb import set_trace as st

class GraphData:
    def __init__(self, nodes, edges, node_dict, inv_node_dict, acc_sys, acc_test, init):
        self.nodes = nodes
        self.edges = edges
        self.node_dict = node_dict
        self.inv_node_dict = inv_node_dict
        self.acc_sys = acc_sys
        self.acc_test = acc_test
        self.init = init
        self.graph = self.setup_graph(nodes, edges)
        self.int = self.acc_test
        self.sink = self.acc_sys

    def setup_graph(self, nodes, edges):
        G = nx.DiGraph()
        G.add_nodes_from(nodes)
        G.add_edges_from(edges)
        return G


def setup_graphs_for_optimization(virtual, prod_ba, sys_virtual):
    # virtual game graph info
    G = setup_nodes_and_edges_for_G(virtual)
    # prod ba info - probably not necessary, if yes return what is needed
    # B_prod = setup_nodes_and_edges_for_prod_ba(prod_ba)
    # virtual system game graph info
    # S = setup_nodes_and_edges_for_S(sys_virtual)
    #
    # for i,j in S.edges:
    #     if i == j:
    #         S.graph.remove_edge(i,j)
    # S.edges = S.graph.edges

    for i, j in G.edges:
        if i == j:
            # st()
            G.graph.remove_edge(i,j)
    G.edges = G.graph.edges
    # st()
    return G#, B_prod, S


def setup_nodes_and_edges_for_S(sys_virtual):
    # setup nodes and map
    nodes = []
    node_dict = {}
    inv_node_dict = {}
    for i, node in enumerate(sys_virtual.nodes):
        nodes.append(i)
        node_dict.update({i: node})
        inv_node_dict.update({node: i})
    # find initial state
    init = []
    for initial in sys_virtual.states.initial:
        init.append(inv_node_dict[initial])
    # find accepting states for system and tester
    acc_sys = []
    acc_test = []
    for i in node_dict.keys():# states are labeled (ts,system)
        if 'accept' in node_dict[i][1]:
            acc_sys.append(i)
    # setup edges
    edges = []
    for edge in sys_virtual.edges:
        edges.append((inv_node_dict[edge[0]],inv_node_dict[edge[1]]))

    S = GraphData(nodes, edges, node_dict, inv_node_dict, acc_sys, None, init)
    return S


def setup_nodes_and_edges_for_prod_ba(prod_ba):
    # setup nodes and map
    nodes = []
    node_dict = {}
    inv_node_dict = {}
    for i, node in enumerate(prod_ba.nodes):
        nodes.append(i)
        node_dict.update({i: node})
        inv_node_dict.update({node: i})
    # find initial state
    init = []
    for initial in prod_ba.states.initial:
        init.append(inv_node_dict[initial])
    # find accepting states for system and tester
    acc_sys = []
    acc_test = []
    for i in node_dict.keys():# states are labeled (tester,system)
        if 'accept' in node_dict[i][0]:
            acc_test.append(i)
        if 'accept' in node_dict[i][1]:
            acc_sys.append(i)
    # setup edges
    edges = []
    for edge in prod_ba.edges:
        edges.append((inv_node_dict[edge[0]],inv_node_dict[edge[1]]))

    B_prod = GraphData(nodes, edges, node_dict, inv_node_dict, acc_sys, acc_test, init)
    return B_prod


def setup_nodes_and_edges_for_G(virtual):
    # setup nodes and map
    nodes = []
    node_dict = {}
    inv_node_dict = {}
    for i, node in enumerate(virtual.nodes):
        nodes.append(i)
        node_dict.update({i: node})
        inv_node_dict.update({node: i})
    # find initial state
    init = []
    for initial in virtual.states.initial:
        init.append(inv_node_dict[initial])
    # find accepting states for system and tester
    acc_sys = []
    acc_test = []
    for i in node_dict.keys():# states are labeled (ts, (tester,system))
        if 'accept' in node_dict[i][1][1]: # check if system goal first, no duplicates
            acc_sys.append(i)
        elif 'accept' in node_dict[i][1][0]:
            acc_test.append(i)
    # setup edges
    edges = []
    for edge in virtual.edges:
        edges.append((inv_node_dict[edge[0]],inv_node_dict[edge[1]]))

    G = GraphData(nodes, edges, node_dict, inv_node_dict, acc_sys, acc_test, init)
    return G

def setup_nodes_and_edges(virtual_game_graph, virtual_sys, b_pi):
    # setup nodes and map
    nodes = []
    node_dict = {}
    inv_node_dict = {}
    for i, node in enumerate(virtual_game_graph.G_initial.nodes):
        nodes.append(i)
        node_dict.update({i: virtual_game_graph.reverse_Sdict[node]})
        inv_node_dict.update({virtual_game_graph.reverse_Sdict[node]: i})
    # find initial state
    init = []
    for initial in virtual_game_graph.I:
        init.append(inv_node_dict[initial])
    # find accepting states for system and tester
    acc_sys = []
    acc_test = []
    for node in nodes:
        if node_dict[node] in virtual_game_graph.sink:
            acc_sys.append(node)
        if node_dict[node] in virtual_game_graph.int:
            acc_test.append(node)
    # setup edges
    edges = []
    for edge in virtual_game_graph.G_initial.edges:
        out_node = virtual_game_graph.reverse_Sdict[edge[0]]
        in_node = virtual_game_graph.reverse_Sdict[edge[1]]
        edges.append((inv_node_dict[out_node],inv_node_dict[in_node]))

    # setup system graph
    S_nodes = []
    S_node_dict = {}
    S_inv_node_dict = {}
    for i, node in enumerate(virtual_sys.G_initial.nodes):
        S_nodes.append(i)
        S_node_dict.update({i: virtual_sys.reverse_Sdict[node]})
        S_inv_node_dict.update({virtual_sys.reverse_Sdict[node]: i})
    # find initial state
    S_init = []
    for initial in virtual_sys.I:
        S_init.append(S_inv_node_dict[initial])
    # find accepting states for system
    S_acc_sys = []
    for node in S_nodes:
        if S_node_dict[node] in virtual_sys.sink:
            S_acc_sys.append(node)
    # setup edges
    S_edges = []
    for edge in virtual_sys.G_initial.edges:
        out_node = virtual_sys.reverse_Sdict[edge[0]]
        in_node = virtual_sys.reverse_Sdict[edge[1]]
        S_edges.append((S_inv_node_dict[out_node],S_inv_node_dict[in_node]))

    GD = GraphData(nodes, edges, node_dict, inv_node_dict, acc_sys, acc_test, init)
    S = GraphData(S_nodes, S_edges, S_node_dict, S_inv_node_dict, S_acc_sys, [], S_init)
    return GD, S
