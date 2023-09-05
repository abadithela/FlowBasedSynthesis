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
import pyomo.environ as pyo
from pyomo.opt import SolverFactory
from feasibility_constraints import add_feasibility_constraints
from initialize_max_flow import initialize_max_flow
from setup_graphs import setup_graphs_for_optimization
from copy import deepcopy

debug = True
init = False

def solve_bilevel(GD, SD):
    cleaned_intermed = [x for x in GD.acc_test if x not in GD.acc_sys]

    # create G and remove self-loops
    G = GD.graph
    to_remove = []
    for i, j in G.edges:
        if i == j:
            to_remove.append((i,j))
    G.remove_edges_from(to_remove)
    S = SD.graph

    # build model and variables
    model = pyo.ConcreteModel()
    model.nodes = G.nodes
    model.edges = G.edges

    # set S,I,T nodes
    src = GD.init
    sink = GD.sink
    intermed = cleaned_intermed

    vars = ['f1_e', 'f2_e', 'd_e']
    model.y = pyo.Var(vars, model.edges, within=pyo.NonNegativeReals)
    model.t = pyo.Var(within=pyo.NonNegativeReals)

    # Introduce SUBMODEL
    # fixed variables defined by the outer player
    fixed_variables = [model.y['d_e',i,j] for i,j in model.edges] # Cut edges
    fixed_variables.extend([model.y['f1_e',i,j] for i,j in model.edges]) # Flow 1
    fixed_variables.extend([model.y['f2_e',i,j] for i,j in model.edges]) # Flow 2
    fixed_variables.extend([model.t]) # 1/F
    # Submodel - variables defined by the inner player
    model.L = SubModel(fixed=fixed_variables)
    model.L.edges = model.edges
    model.L.nodes = model.nodes
    model.L.f3 = pyo.Var(model.L.edges, within=pyo.NonNegativeReals) # Flow 3 (from s to t not through i)

    # Add constraints that system will always have a path
    model = add_feasibility_constraints(model, GD, SD)
    # model = add_static_obstacle_constraints(model, GD)

    if init: # initialize the flows with valid max flow
        f1_init, f2_init, f3_init, t_init = initialize_max_flow(G, src, intermed, sink)

        for (i,j) in model.edges:
            model.y['d_e', i, j] = 0
            model.y['f1_e', i, j] = f1_init[(i,j)]
            model.y['f2_e', i, j] = f2_init[(i,j)]
            model.L.f3[i, j] = f3_init[(i,j)]
        model.t = t_init

    # Objective - minimize 1/F + lambda*f_3/F
    def mcf_flow(model):
        lam = len(model.edges)
        flow_3 = sum(model.L.f3[i,j] for (i, j) in model.L.edges if i in src)
        # cut_value = sum(model.y['d_e', (i,j)] for (i,j) in model.edges)
        return model.t + lam*flow_3# + cut_value

    model.o = pyo.Objective(rule=mcf_flow, sense=pyo.minimize)

    # Constraints
    # Maximize the flow into the sink
    def flow_src1(model):
        return 1 <= sum(model.y['f1_e', i,j] for (i, j) in model.edges if i in src)
    def flow_src2(model):
        return 1 <= sum(model.y['f2_e', i,j] for (i, j) in model.edges if i in intermed)
    model.min_constr1 = pyo.Constraint(rule=flow_src1)
    model.min_constr2 = pyo.Constraint(rule=flow_src2)

    # capacity constraints
    def capacity1(model, i, j):
        return model.y['f1_e',i, j] <= model.t
    def capacity2(model, i, j):
        return model.y['f2_e', i, j] <= model.t
    model.cap1 = pyo.Constraint(model.edges, rule=capacity1)
    model.cap2 = pyo.Constraint(model.edges, rule=capacity2)

    # conservation constraints
    def conservation1(model, l):
        if l in src or l in intermed:
            return pyo.Constraint.Skip
        incoming  = sum(model.y['f1_e', i,j] for (i,j) in model.edges if j == l)
        outgoing = sum(model.y['f1_e',i,j] for (i,j) in model.edges if i == l)
        return incoming == outgoing
    model.cons1 = pyo.Constraint(model.nodes, rule=conservation1)

    def conservation2(model, l):
        if l in intermed or l in sink:
            return pyo.Constraint.Skip
        incoming  = sum(model.y['f2_e', i,j] for (i,j) in model.edges if j == l)
        outgoing = sum(model.y['f2_e', i,j] for (i,j) in model.edges if i == l)
        return incoming == outgoing
    model.cons2 = pyo.Constraint(model.nodes, rule=conservation2)

    # no flow into sources and out of sinks
    def no_in_source1(model, i,j):
        if j in src:
            return model.y['f1_e',i,j] == 0
        else:
            return pyo.Constraint.Skip
    model.no_in_source1 = pyo.Constraint(model.edges, rule=no_in_source1)
    # nothing leaves sink
    def no_out_sink1(model, i,j):
        if i in intermed:
            return model.y['f1_e', i,j] == 0
        else:
            return pyo.Constraint.Skip
    model.no_out_sink1 = pyo.Constraint(model.edges, rule=no_out_sink1)
    # =================================================================== #
    def no_in_source2(model, i,j):
        if j in intermed:
            return model.y['f2_e',i,j] == 0
        else:
            return pyo.Constraint.Skip
    model.no_in_source2 = pyo.Constraint(model.edges, rule=no_in_source2)

    # nothing leaves sink
    def no_out_sink2(model, i,j):
        if i in sink:
            return model.y['f2_e',i,j] == 0
        else:
            return pyo.Constraint.Skip
    model.no_out_sink2 = pyo.Constraint(model.edges, rule=no_out_sink2)
    # =================================================================== #

    # If the edge is cut -> no flow
    def cut_cons1(model, i, j):
        return model.y['f1_e', i, j] + model.y['d_e', i, j]<= model.t
    model.cut_cons1 = pyo.Constraint(model.edges, rule=cut_cons1)

    def cut_cons2(model,  i, j):
        return model.y['f2_e', i, j] + model.y['d_e', i, j]<= model.t
    model.cut_cons2 = pyo.Constraint(model.edges, rule=cut_cons2)

    # SUBMODEL
    # Objective - Maximize the flow into the sink
    def flow_sink(model):
        return sum(model.f3[i,j] for (i, j) in model.edges if j in sink)
    model.L.o = pyo.Objective(rule=flow_sink, sense=pyo.maximize)

    # Capacity constraints
    def capacity(mdl, i, j):
        return mdl.f3[i, j] <= model.t
    model.L.cap3 = pyo.Constraint(model.L.edges, rule=capacity)

    # Conservation constraints
    def conservation(model, l):
        if l in sink or l in src:
            return pyo.Constraint.Skip
        incoming  = sum(model.f3[i,j] for (i,j) in model.edges if j == l)
        outgoing = sum(model.f3[i,j] for (i,j) in model.edges if i == l)
        return incoming == outgoing
    model.L.cons3 = pyo.Constraint(model.L.nodes, rule=conservation)

    # nothing enters the source
    def no_in_source(model, i,j):
        if j in src:
            return model.f3[i,j] == 0
        else:
            return pyo.Constraint.Skip
    model.L.no_in_source3 = pyo.Constraint(model.L.edges, rule=no_in_source)

    # nothing leaves sink
    def no_out_sink(model, i,j):
        if i in sink:
            return model.f3[i,j] == 0
        else:
            return pyo.Constraint.Skip
    model.L.no_out_sink3 = pyo.Constraint(model.L.edges, rule=no_out_sink)

    # nothing enters the intermediate or leaves the intermediate
    def no_in_interm(model, i,j):
        if j in intermed:
            return model.f3[i,j] == 0
        else:
            return pyo.Constraint.Skip
    model.L.no_in_interm = pyo.Constraint(model.L.edges, rule=no_in_interm)

    def no_out_interm(model, i,j):
        if i in intermed:
            return model.f3[i,j] == 0
        else:
            return pyo.Constraint.Skip
    model.L.no_out_interm = pyo.Constraint(model.L.edges, rule=no_out_interm)

    # Cut constraints for flow 3
    def cut_cons(mdl, i, j):
        return mdl.f3[i,j] + model.y['d_e',i,j]<= model.t
    model.L.cut_cons = pyo.Constraint(model.L.edges, rule=cut_cons)

    print(" ==== Successfully added objective and constraints! ==== ")
    if debug:
        model.pprint()
    # st()

    with Solver('pao.pyomo.REG') as solver:
        results = solver.solve(model, tee=True)

    # model.pprint()
    f1_e = dict()
    f2_e = dict()
    f3_e = dict()
    d_e = dict()
    F = 0

    for (i,j) in model.edges:
        F = (1.0)/(model.t.value)
        f1_e.update({(i,j): model.y['f1_e', i,j].value*F})
        f2_e.update({(i,j): model.y['f2_e', i,j].value*F})
        d_e.update({(i,j): model.y['d_e', i,j].value*F})
    for (i,j) in model.L.edges:
        f3_e.update({(i,j): model.L.f3[i,j].value*F})

    for key in d_e.keys():
        print('{0} to {1} at {2}'.format(GD.node_dict[key[0]], GD.node_dict[key[1]],d_e[key]))
    if debug:
        st()
    return f1_e, f2_e, f3_e, d_e, F
