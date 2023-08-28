import sys
sys.path.append('..')
import numpy as np
from ipdb import set_trace as st
import networkx as nx
import pdb
from three_flows import solve_bilevel as solve_bilevel_three_flows
from two_flows import solve_bilevel as solve_bilevel_two_flows
from two_flows_nonneg_vars import solve_bilevel as solve_bilevel_two_flows_nonneg_vars
from setup_graphs import GraphData

def graph1():
    # setup nodes and map
    # Node labels:: 1: S, 4,5,6: I, 7: T
    # Edges: (1,2), (2,1), (1,3), (3,1), (2,7), (3,7), (2,4), (3,5), (4,6), (5,6), (6,7)
    n = 7
    nodes = [i for i in range(1,n+1)]
    node_dict = {}
    inv_node_dict = {}
    for i in range(1,n+1):
        node_dict[i]=i
        inv_node_dict[i] = i
    # find initial state
    init = [1]
    
    # find accepting states for system and tester
    acc_sys = [7]
    acc_test = [4,5,6]
    
    # setup edges
    edges = [(1,2), (2,1), (1,3), (3,1), (2,7), (3,7), (2,4), (3,5), (4,6), (5,6), (6,7)]

    GD = GraphData(nodes, edges, node_dict, inv_node_dict, acc_sys, acc_test, init)
    return GD

def graph2():
    # setup nodes and map
    # Node labels:: 1: S, 3,5,6: I, 7: T
    # Edges: (1,2), (2,3), (3,3), (1,4), (4,5), (4,7), (5,6), (6,7)
    n = 7
    nodes = [i for i in range(1,n+1)]
    node_dict = {}
    inv_node_dict = {}
    for i in range(1,n+1):
        node_dict[i]=i
        inv_node_dict[i] = i
    # find initial state
    init = [1]
    
    # find accepting states for system and tester
    acc_sys = [7]
    acc_test = [3,5,6]
    
    # setup edges
    edges = [(1,2), (2,3), (3,3), (1,4), (4,5), (4,7), (5,6), (6,7)]

    GD = GraphData(nodes, edges, node_dict, inv_node_dict, acc_sys, acc_test, init)
    return GD

def call_pyomo_three_flows(G):
    ftest1, ftest2, fsys, d, F = solve_bilevel_three_flows(G)
    cuts = [x for x in d.keys() if d[x] >= 0.9]
    pdb.set_trace()
    flow = F
    bypass_flow = sum([ftest[j] for j in ftest.keys() if j[1] in G.sink])
    print('Cut {} edges in the virtual game graph.'.format(len(cuts)))
    print('The max flow through I is {}'.format(F))
    print('The bypass flow is {}'.format(bypass_flow))

    for cut in cuts:
        print('Cutting {0} to {1}'.format(G.node_dict[cut[0]], G.node_dict[cut[1]]))
    # st()
    return cuts, flow, bypass_flow

def call_pyomo_two_flows(G):
    ftest, fsys, d, F = solve_bilevel_two_flows(G)
    cuts = [x for x in d.keys() if d[x] >= 0.9]
    pdb.set_trace()
    flow = F
    bypass_flow = sum([fsys[j] for j in fsys.keys() if j[1] in G.sink])
    print('Cut {} edges in the virtual game graph.'.format(len(cuts)))
    print('The max flow through I is {}'.format(F))
    print('The bypass flow is {}'.format(bypass_flow))

    for cut in cuts:
        print('Cutting {0} to {1}'.format(G.node_dict[cut[0]], G.node_dict[cut[1]]))
    # st()
    return cuts, flow, bypass_flow

def call_pyomo_two_flows_nonneg_vars(G):
    ftest, fsys, d, F = solve_bilevel_two_flows_nonneg_vars(G)
    cuts = [x for x in d.keys() if d[x] >= 0.9]
    pdb.set_trace()
    flow = F
    bypass_flow = sum([fsys[j] for j in fsys.keys() if j[1] in G.sink])
    print('Cut {} edges in the virtual game graph.'.format(len(cuts)))
    print('The max flow through I is {}'.format(F))
    print('The bypass flow is {}'.format(bypass_flow))

    for cut in cuts:
        print('Cutting {0} to {1}'.format(G.node_dict[cut[0]], G.node_dict[cut[1]]))
    # st()
    return cuts, flow, bypass_flow

def get_graph(nodes, edges):
    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    return G


def find_cuts_three_flows():
    G = graph2()
    cuts = []
    cuts, flow, bypass = call_pyomo_three_flows(G)
    st()
    return G,cuts

def find_cuts_two_flows():
    G = graph2()
    #
    cuts = []
    cuts, flow, bypass = call_pyomo_two_flows(G)
    st()
    return G,cuts

if __name__ == '__main__':
    find_cuts_two_flows()
