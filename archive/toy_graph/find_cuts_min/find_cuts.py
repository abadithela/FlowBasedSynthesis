import sys
sys.path.append('..')
import numpy as np
from ipdb import set_trace as st
import networkx as nx
import pdb
from cut_flow_fcns import solve_min
from inner_min import solve_inner_min
# from construct_automata import get_gamegraph, construct_automata
# from runnerblocker_network import RunnerBlockerNetwork
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
    edges = [(1,2), (2,1), (1,3), (3,1), (2,7), (3,7), (2,4), (3,5), (4,6), (5,6), (6,7), (5,7)]

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

def call_pyomo(GD):
    ftest, fsys, d, F = solve_min(GD)
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
    G = graph1()
    cuts = []
    cuts, flow, bypass = call_pyomo(G)
    st()
    G = get_graph(nodes, edges) # virtual graph in networkx graph form
    st()
    return GD,cuts

def debug_inner_min():
    G = graph2()
    cuts = []
    lam, mu = solve_inner_min(GD)
    st()

if __name__ == '__main__':
    find_cuts()
