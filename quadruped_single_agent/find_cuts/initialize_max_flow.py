# Compute the max flow without any obstacles to initialize the optimization
# J. Graebener

import sys
sys.path.append('..')
import numpy as np
from ipdb import set_trace as st
from collections import OrderedDict as od
import _pickle as pickle
import os
import networkx as nx
from pao.pyomo import *
import pyomo.environ as pyo
from pyomo.opt import SolverFactory
from copy import deepcopy
import matplotlib.pyplot as plt


def initialize_max_flow(G, src, intermed, sink):
    f1_e = max_flow(G, src, intermed)
    f2_e = max_flow(G, intermed, sink)

    flow1 = sum([f1_e[(i,j)] for (i,j) in f1_e.keys() if j in intermed])
    flow2 = sum([f2_e[(i,j)] for (i,j) in f2_e.keys() if j in sink])
    flow = min(flow1, flow2)

    # remove intermediate nodes
    G_minus_I = deepcopy(G)
    to_remove = []
    for edge in G.edges:
        if edge[0] in intermed or edge[1] in intermed:
            to_remove.append(edge)
    G_minus_I.remove_edges_from(to_remove)

    f3_e = max_flow(G_minus_I, src, sink)

    for edge in G.edges:
        f1_e.update({edge: f1_e[edge]/flow})
        f2_e.update({edge: f2_e[edge]/flow})
        if edge in G_minus_I.edges:
            f3_e.update({edge: f3_e[edge]/flow})
        else:
            f3_e.update({edge: 0.0})

    return f1_e, f2_e, f3_e

def max_flow(graph, start, goal):
    model = pyo.ConcreteModel()
    model.nodes = graph.nodes
    model.edges = graph.edges

    model.f = pyo.Var(model.edges, within=pyo.NonNegativeReals)

    # Objective: Maximize the flow into the sink
    def flow_sink(model):
        return sum(model.f[(i,j)] for (i, j) in model.edges if j in goal)
    model.total_flow = pyo.Objective(rule=flow_sink, sense=pyo.maximize)

    # capacity constraint
    def capacity(model, i, j):
        return model.f[(i,j)] <= 1
    model.cap = pyo.Constraint(model.edges, rule=capacity)

    # conservation constraint
    def conservation(model, k):
        if k in start or k in goal:
            return pyo.Constraint.Skip
        if len(graph.out_edges(k)) == 0 and len(graph.in_edges(k)) == 0:
            return pyo.Constraint.Skip
        inFlow  = sum(model.f[(i,j)] for (i,j) in model.edges if j == k)
        outFlow = sum(model.f[(i,j)] for (i,j) in model.edges if i == k)
        return inFlow == outFlow
    model.cons = pyo.Constraint(model.nodes, rule=conservation)

    # # no flow into sources and out of sinks
    def no_in_source(model, i,j):
        if j in start:
            return model.f[(i,j)] == 0.0
        else:
            return pyo.Constraint.Skip
    model.no_in_source = pyo.Constraint(model.edges, rule=no_in_source)
    # nothing leaves sink
    def no_out_sink(model, i,j):
        if i in goal:
            return model.f[(i,j)] == 0.0
        else:
            return pyo.Constraint.Skip
    model.no_out_sink = pyo.Constraint(model.edges, rule=no_out_sink)
    # =================================================================== #
    print(" ==== Successfully added objective and constraints! ==== ")
    model.pprint()

    opt = SolverFactory('glpk')
    if not opt:
        print('Problem loading solver')
        st()

    result = opt.solve(model, tee = True)

    f_e = dict()
    for (i,j) in model.edges:
        f_e.update({(i,j): model.f[i,j].value})

    return f_e
