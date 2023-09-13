import sys
sys.path.append('..')
import numpy as np
from ipdb import set_trace as st
import networkx as nx
import pdb
from cut_flow_fcns import solve_bilevel
# from construct_automata import get_gamegraph, construct_automata
# from runnerblocker_network import RunnerBlockerNetwork
from construct_automata.main import quad_test_sync
from setup_graphs import GraphData

def setup_automata(network):
    ts, prod_ba, virtual, sys_virtual, snr_to_nr, snr_to_label, label_to_snr = create_ts_automata_and_virtual_game_graph(network)
    return virtual, sys_virtual, snr_to_nr, snr_to_label, label_to_snr

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

def call_pyomo(GD, S):

    ftest, fsys, d, F = solve_bilevel(GD, S)
    cuts = [x for x in d.keys() if d[x] >= 0.9]
    # pdb.set_trace()
    flow = F
    bypass_flow = sum([fsys[j] for j in fsys.keys() if j[1] in GD.sink])
    print('Cut {} edges in the virtual game graph.'.format(len(cuts)))
    print('The max flow through I is {}'.format(F))
    print('The bypass flow is {}'.format(bypass_flow))

    for cut in cuts:
        print('Cutting {0} to {1}'.format(GD.node_dict[cut[0]], GD.node_dict[cut[1]]))
    # st()
    return cuts, flow, bypass_flow


def get_graph(nodes, edges):
    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    return G


def find_cuts():

    virtual, system, b_pi, virtual_sys = quad_test_sync()

    # network = RunnerBlockerNetwork([1,2,3])
    # ts, prod_ba, virtual, sys_virtual, state_map = construct_automata(network)

    GD, S = setup_nodes_and_edges(virtual, virtual_sys, b_pi)
    #
    cuts = []
    cuts, flow, bypass = call_pyomo(GD, S)
    st()

    # G = get_graph(nodes, edges) # virtual graph in networkx graph form
    # prune the dead ends
    # G, new_cuts = postprocess_cuts(GD, cuts)
    st()
    return GD,cuts



if __name__ == '__main__':
    find_cuts()
