# find max flow given the graph, start, goal and the cuts

import sys
sys.path.append('..')
import numpy as np
import networkx as nx
from pao.pyomo import *
import pyomo.environ as pyo
from pyomo.opt import SolverFactory
from ipdb import set_trace as st

def max_flow_value(graph, start, goal, cuts):
    max_f = max_flow(graph, start, goal, cuts)
    max_flow_val = sum(max_f[i,j] for (i,j) in graph.edges if i in start)
    return max_flow_val

def max_flow(graph, start, goal, cuts):

    model = pyo.ConcreteModel()
    model.nodes = graph.nodes
    model.edges = graph.edges

    if not cuts:
        cuts = dict()
        for (i,j) in model.edges:
            cuts.update({(i,j): 0})

    model.f = pyo.Var(model.edges, within=pyo.NonNegativeReals)

    # Objective: Maximize the flow into the sink
    def flow_sink(model):
        return sum(model.f[(i,j)] for (i, j) in model.edges if j in goal)
    model.total_flow = pyo.Objective(rule=flow_sink, sense=pyo.maximize)

    # capacity constraint
    def capacity(model, i, j):
        return model.f[(i,j)] <= 1 - cuts[i,j]
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

    opt = SolverFactory('glpk')
    if not opt:
        print('Problem loading solver')
        st()

    result = opt.solve(model, tee = True)

    f_e = dict()
    for (i,j) in model.edges:
        f_e.update({(i,j): model.f[i,j].value})

    return f_e
