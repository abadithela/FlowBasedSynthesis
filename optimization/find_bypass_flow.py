# find fsys given edge cuts d
# J. Graebener

import sys
sys.path.append('..')
import numpy as np
from ipdb import set_trace as st
import os
import networkx as nx
from pao.pyomo import *
import pyomo.environ as pyo
from pyomo.opt import SolverFactory
from copy import deepcopy
from optimization.max_flow import max_flow

def find_fby(GD, cuts):

    src = GD.init
    sink = GD.sink
    intermed = [x for x in GD.acc_test if x not in GD.acc_sys]

    G = GD.graph

    # remove self-loops
    to_remove = []
    for i, j in G.edges:
        if i == j:
            to_remove.append((i,j))
    G.remove_edges_from(to_remove)

    # remove intermediate nodes
    G_minus_I = deepcopy(G)
    to_remove = []
    for edge in G.edges:
        if edge[0] in intermed or edge[1] in intermed:
            to_remove.append(edge)
    G_minus_I.remove_edges_from(to_remove)

    # find the max bypass flow on the graph without the intermediate nodes
    fby_e = max_flow(G_minus_I, src, sink, cuts)

    return fby_e

#
# def max_flow(graph, start, goal, cuts):
#
#     model = pyo.ConcreteModel()
#     model.nodes = graph.nodes
#     model.edges = graph.edges
#
#     if not cuts:
#         cuts = dict()
#         for (i,j) in model.edges:
#             cuts.update({(i,j): 0})
#
#     model.f = pyo.Var(model.edges, within=pyo.NonNegativeReals)
#
#     # Objective: Maximize the flow into the sink
#     def flow_sink(model):
#         return sum(model.f[(i,j)] for (i, j) in model.edges if j in goal)
#     model.total_flow = pyo.Objective(rule=flow_sink, sense=pyo.maximize)
#
#     # capacity constraint
#     def capacity(model, i, j):
#         return model.f[(i,j)] <= 1 - cuts[i,j]
#     model.cap = pyo.Constraint(model.edges, rule=capacity)
#
#     # conservation constraint
#     def conservation(model, k):
#         if k in start or k in goal:
#             return pyo.Constraint.Skip
#         if len(graph.out_edges(k)) == 0 and len(graph.in_edges(k)) == 0:
#             return pyo.Constraint.Skip
#         inFlow  = sum(model.f[(i,j)] for (i,j) in model.edges if j == k)
#         outFlow = sum(model.f[(i,j)] for (i,j) in model.edges if i == k)
#         return inFlow == outFlow
#     model.cons = pyo.Constraint(model.nodes, rule=conservation)
#
#     # # no flow into sources and out of sinks
#     def no_in_source(model, i,j):
#         if j in start:
#             return model.f[(i,j)] == 0.0
#         else:
#             return pyo.Constraint.Skip
#     model.no_in_source = pyo.Constraint(model.edges, rule=no_in_source)
#     # nothing leaves sink
#     def no_out_sink(model, i,j):
#         if i in goal:
#             return model.f[(i,j)] == 0.0
#         else:
#             return pyo.Constraint.Skip
#     model.no_out_sink = pyo.Constraint(model.edges, rule=no_out_sink)
#     # =================================================================== #
#     # print(" ==== Successfully added objective and constraints! ==== ")
#     # model.pprint()
#
#     opt = SolverFactory('glpk')
#     if not opt:
#         print('Problem loading solver')
#         st()
#
#     result = opt.solve(model, tee = True)
#
#     f_e = dict()
#     for (i,j) in model.edges:
#         f_e.update({(i,j): model.f[i,j].value})
#
#     return f_e
