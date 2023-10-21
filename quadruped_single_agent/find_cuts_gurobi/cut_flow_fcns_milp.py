# Solve the bilevel optimization as LFP (Linear Fractional Program) to
# route the flow through the vertices satisfying the test specification
# J. Graebener, A. Badithela

import sys
sys.path.append('..')
import numpy as np
from ipdb import set_trace as st
from collections import OrderedDict as od
import _pickle as pickle
import os
import networkx as nx
from pao.pyomo import *
import pao
import pdb
import pyomo.environ as pyo
from pyomo.opt import SolverFactory
from feasibility_constraints import add_feasibility_constraints
from setup_graphs import setup_graphs_for_optimization
from initialize_max_flow import initialize_max_flow
from copy import deepcopy

debug = False
init = False

chosen_solver = 'gurobi'

def solve_min(GD, SD):
    cleaned_intermed = [x for x in GD.acc_test if x not in GD.acc_sys]
    # create G and remove self-loops
    G = GD.graph
    to_remove = []
    for i, j in G.edges:
        if i == j:
            to_remove.append((i,j))
    G.remove_edges_from(to_remove)

    # remove intermediate nodes
    G_minus_I = deepcopy(G)
    to_remove = []
    for edge in G.edges:
        if edge[0] in cleaned_intermed or edge[1] in cleaned_intermed:
            to_remove.append(edge)
    G_minus_I.remove_edges_from(to_remove)

    # create S and remove self-loops
    S = SD.graph
    to_remove = []
    for i, j in S.edges:
        if i == j:
            to_remove.append((i,j))
    S.remove_edges_from(to_remove)

    model = pyo.ConcreteModel()
    model.nodes = G.nodes
    model.edges = G.edges
    model.edges_without_I = G_minus_I.edges
    model.nodes_without_I = G_minus_I.nodes

    src = GD.init
    sink = GD.sink
    inter = cleaned_intermed

    # 'ft': tester flow, and d: cut values
    model.f = pyo.Var(model.edges, within=pyo.NonNegativeReals)
    # model.t = pyo.Var(within=pyo.NonNegativeReals)

    # model variables for the dual
    model.d = pyo.Var(model.edges_without_I, within=pyo.Binary)
    model.m = pyo.Var(model.nodes_without_I, within=pyo.NonNegativeReals)

    # Add constraints that system will always have a path
    model = add_feasibility_constraints(model, GD, SD)


    # Objective - minimize (1-gamma)*t + gamma*sum(lam*(t-de))
    def obj(model):
        flow = sum(model.f[i,j] for (i,j) in model.edges if i in src)
        ncuts = sum(model.d[i,j] for (i,j) in model.edges if (i,j) in G_minus_I.edges)
        return flow - 1e-3*ncuts
    model.o = pyo.Objective(rule=obj, sense=pyo.maximize)

    # Constraints
    # Maximize the flow into the sink
    def flow_src_test(model):
        return 1 == sum(model.f[i,j] for (i, j) in model.edges if i in src)
    model.min_constr = pyo.Constraint(rule=flow_src_test)

    def capacity_test(model, i, j):
        return model.f[i, j] <= 1
    model.cap_test = pyo.Constraint(model.edges, rule=capacity_test)

    # conservation constraints
    def conservation_test(model, l):
        if l in src or l in sink:
            return pyo.Constraint.Skip
        incoming  = sum(model.f[i,j] for (i,j) in model.edges if j == l)
        outgoing = sum(model.f[i,j] for (i,j) in model.edges if i == l)
        return incoming == outgoing
    model.cons_test = pyo.Constraint(model.nodes, rule=conservation_test)

    # no flow into sources and out of sinks
    def no_in_source_test(model, i,j):
        if j in src:
            return model.f[i,j] == 0
        else:
            return pyo.Constraint.Skip
    model.no_in_source_test = pyo.Constraint(model.edges, rule=no_in_source_test)

    # nothing leaves sink
    def no_out_sink_test(model, i,j):
        if i in sink:
            return model.f[i,j] == 0
        else:
            return pyo.Constraint.Skip
    model.no_out_sink_test = pyo.Constraint(model.edges, rule=no_out_sink_test)

    # If the edge is cut -> no flow
    def cut_cons_test(model, i, j):
        return model.f[i, j] + model.d[i, j]<= 1
    model.cut_cons_test = pyo.Constraint(model.edges_without_I, rule=cut_cons_test)

    # constraints for inner dual problem
    # partition constraint for max flow dual
    model.max_flow_partitions = pyo.ConstraintList()
    node_list = list(G_minus_I.nodes)
    for count, i in enumerate(node_list):
        for j in node_list[count+1:]:
            if i in src and j in sink:
                expression = model.m[i] - model.m[j] >= 1
                model.max_flow_partitions.add(expr = expression)
            elif i in sink and j in src:
                expression = model.m[j] - model.m[i] >= 1
                model.max_flow_partitions.add(expr = expression)

    # max flow cut constraint
    def max_flow_cut(model, i,j):
        return model.d[i,j] - model.m[i] + model.m[j] >= 0
    model.max_flow_cut = pyo.Constraint(model.edges_without_I, rule=max_flow_cut)

    if debug:
        print(" ==== Successfully added objective and constraints! ==== ")
        model.pprint()

    if chosen_solver == 'gurobi':
        opt = SolverFactory("gurobi", solver_io="python")
        opt.options['NonConvex'] = 2
    elif chosen_solver == 'cplex':
        opt = SolverFactory("cplex", executable="/Applications/CPLEX_Studio2211/cplex/bin/x86-64_osx/cplex")
        opt.options['optimalitytarget']=3

    opt.solve(model, tee= True)

    if debug:
        model.display()

    ftest = dict()
    d = dict()
    mu = dict()

    for (i,j) in model.edges:
        ftest.update({(i,j): model.f[i,j].value})
    F = sum(model.f[i,j].value for (i,j) in model.edges if i in src)

    for (i,j) in model.edges_without_I:
        d.update({(i,j): model.d[i,j].value})
    for k in model.nodes_without_I:
        mu.update({(k): model.m[k].value})

    for key in d.keys():
        print('{0} to {1} at {2}'.format(GD.node_dict[key[0]], GD.node_dict[key[1]],d[key]))

    return ftest, d, F
