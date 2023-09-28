import sys
sys.path.append('..')
sys.path.append('../algorithms/')
import numpy as np
from ipdb import set_trace as st
from collections import OrderedDict as od
import _pickle as pickle
import os
import networkx as nx
import matplotlib.pyplot as plt
import pdb
from mogd_problem_data import *

def initialize(nodes, edges):
    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    # remove self loops
    for i,j in edges:
        if i == j:
            G.remove_edge(i,j)
    nodes = list(G.nodes())
    nodes_keys = {k: v for k,v in enumerate(nodes)}
    edges = list(G.edges())
    edges_keys = {k: e for k,e in enumerate(edges)}
    return G, nodes_keys, edges_keys

def parse_solution(xtraj, ytraj, edges_keys):
    ne = len(edges_keys)
    f1_e_hist = [dict() for k in range(len(xtraj))]
    f2_e_hist = [dict() for k in range(len(xtraj))]
    f3_e_hist = [dict() for k in range(len(xtraj))]
    d_e_hist = [dict() for k in range(len(xtraj))]
    F_hist = [0 for k in range(len(xtraj))]
    for t in range(len(xtraj)):
        x = xtraj[t]
        y = ytraj[t]
        F_hist[t] = 1/x[-1]
        for idx, val in edges_keys.items():
            f1_e_hist[t].update({val: x[idx]*F_hist[t]})
            f2_e_hist[t].update({val: x[ne + idx]*F_hist[t]})
            d_e_hist[t].update({val: x[2*ne + idx]*F_hist[t]})
            f3_e_hist[t].update({val: y[val]*F_hist[t]})
    return f1_e_hist, f2_e_hist, f3_e_hist, d_e_hist, F_hist

def process_nodes(init, intermed, goal):
    if isinstance(init, list):
        src = init
    else:
        src = [init]
    if isinstance(intermed, list):
        int = intermed
    else:
        int = [intermed]
    if isinstance(goal, list):
        sink = goal
    else:
        sink = [goal]
    return src, int, sink

def solve_mogd(nodes,edges, init, intermed, goal, node_dict, state_map, lite=False):
    G, nodes_keys, edges_keys = initialize(nodes, edges)
    x0, y0 = get_candidate_flows(G, edges_keys, init, intermed, goal)

    src, int, sink = process_nodes(init, intermed, goal)
    Aeq, beq, eq_cons_names, Aineq, bineq, ineq_cons_names = all_constraints(edges_keys, nodes_keys, src, int, sink)

    # Aeq_proj, beq_proj, eq_cons_names_proj, Aineq_proj, bineq_proj, ineq_cons_names_proj = proj_constraints(edges_keys, nodes_keys, src, int, sink)

    c1, c2 = objective(edges_keys)
    ne = len(list(edges_keys.keys())) # number of edges
    T = 500
    eta = 0.01
    reg = 10

    if not lite:
        xtraj, ytraj = mogd(T, x0, eta, c1, c2, Aeq, beq, Aineq, bineq, Aeq_proj, beq_proj, Aineq_proj, bineq_proj, eq_cons_names, ineq_cons_names, edges_keys, nodes_keys, src, sink, int, LAMBDA=reg)
    else:
        xtraj, ytraj = mogd_lite(T, x0, eta, c1, c2, Aeq, beq, Aineq, bineq, Aeq_proj, beq_proj, Aineq_proj, bineq_proj, eq_cons_names, ineq_cons_names, edges_keys, nodes_keys, src, sink, int, LAMBDA=reg)

    f1_e_hist, f2_e_hist, f3_e_hist, d_e_hist, F_hist = parse_solution(xtraj, ytraj, edges_keys)
    return f1_e_hist[-1], f2_e_hist[-1], f3_e_hist[-1], d_e_hist[-1], F_hist[-1]
