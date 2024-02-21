'''
This file uses the products from flow_constraints and saves the graph
with the highlighted cuts.
'''
import sys
sys.path.append('..')
import numpy as np
from ipdb import set_trace as st
import networkx as nx
import pdb
from construct_automata.main import quad_test_sync
from flow_constraints.plotting import highlight_cuts

try:
    from cut_flow_fcns import solve_bilevel
    from setup_graphs import GraphData
    from constraint_specs import get_history_vars, history_var_dynamics, occupy_cuts, do_not_excessively_constrain
except:
    from find_cuts_two_flows.cut_flow_fcns import solve_bilevel
    from find_cuts_two_flows.setup_graphs import GraphData
    from find_cuts_two_flows.constraint_specs import get_history_vars, history_var_dynamics, occupy_cuts, do_not_excessively_constrain


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

# def highlight_cuts(cuts, GD, SD, virtual, virtual_sys):
#     annot_cuts = [(GD.node_dict[cut[0]], GD.node_dict[cut[1]]) for cut in cuts]
#     sys_cuts = [(GD.node_dict[cut[0]][0], GD.node_dict[cut[1]][0]) for cut in cuts]
#     sys_cuts_annot = [((cut[0], q1), (cut[1], q2)) for cut in sys_cuts for q1 in virtual_sys.AP for q2 in virtual_sys.AP]
#
#     virtual.plot_with_highlighted_edges(annot_cuts, "imgs/virtual_with_cuts")
#     virtual_sys.plot_with_highlighted_edges(sys_cuts_annot, "imgs/virtual_sys_with_cuts")

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

    GD, SD = setup_nodes_and_edges(virtual, virtual_sys, b_pi)
    #
    cuts = []
    cuts, flow, bypass = call_pyomo(GD, SD)

    highlight_cuts(cuts, GD, SD, virtual, virtual_sys)
    st()

    return GD,cuts


if __name__ == '__main__':
    find_cuts()
