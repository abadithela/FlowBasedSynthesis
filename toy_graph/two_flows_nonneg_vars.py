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
from setup_graphs import setup_graphs_for_optimization
from copy import deepcopy

debug = True
debug_disjointed_graph1 = False
debug_disjointed_graph2 = False
add_min_flow_constr = False

assert not(debug_disjointed_graph1 and debug_disjointed_graph2) # Not debugging both graphs at once

def solve_bilevel(GD):
    cleaned_intermed = [x for x in GD.acc_test if x not in GD.acc_sys]
    G = GD.graph

    model = pyo.ConcreteModel()
    model.nodes = G.nodes
    model.edges = G.edges
    ne = len(model.edges)

    src = GD.init
    sink = GD.sink
    inter = GD.int

    # 'ft': tester flow, and d: cut values
    vars = ['ft', 'd']
    model.y = pyo.Var(vars, model.edges, within=pyo.NonNegativeReals)
    model.t = pyo.Var(within=pyo.NonNegativeReals)

    # Introduce SUBMODEL
    # fixed variables defined by the upper level (tester)
    fixed_variables = [model.y['d',i,j] for i,j in model.edges] # Cut edges
    fixed_variables.extend([model.y['ft',i,j] for i,j in model.edges]) # Flow 1
    fixed_variables.extend([model.t]) # 1/F
    # Submodel - variables defined by the system under test
    model.L = SubModel(fixed=fixed_variables)
    model.L.edges = model.edges
    model.L.nodes = model.nodes
    model.L.fs = pyo.Var(model.L.edges, within=pyo.NonNegativeReals) # Flow 3 (from s to t not through i)

    # Add constraints that system will always have a path
    # model = add_feasibility_constraints(model, GD, SD)

    # Objective - minimize 1/F + lambda*f_sys/F
    def mcf_flow(model):
        lam = 1
        bypass = sum(model.L.fs[i,j] for (i, j) in model.L.edges if i in src)
        cut_value = sum(model.y['d', i,j] for (i, j) in model.edges)
        return model.t + ne*bypass + cut_value
    model.o = pyo.Objective(rule=mcf_flow, sense=pyo.minimize)

    # Constraints
    # Non-negativity constraints:
    def nonneg_cuts_constr(model, i,j):
        return model.y['d',i,j] >= 0
    model.nonneg_cuts = pyo.Constraint(model.edges, rule=nonneg_cuts_constr)

    def nonneg_flow_constr(model, i,j):
        return model.y['ft',i,j] >= 0
    model.nonneg_flow = pyo.Constraint(model.edges, rule=nonneg_flow_constr)

    # Maximize the flow into the sink
    if add_min_flow_constr:
        def flow_src_test(model):
            return 1 <= sum(model.y['ft', i,j] for (i, j) in model.edges if i in src)
        model.min_constr = pyo.Constraint(rule=flow_src_test)

    def capacity_test(model, i, j):
        return model.y['ft',i, j] <= model.t
    model.cap_test = pyo.Constraint(model.edges, rule=capacity_test)

    # conservation constraints
    def conservation_test(model, l):
        if l in src or l in sink:
            return pyo.Constraint.Skip
        incoming  = sum(model.y['ft', i,j] for (i,j) in model.edges if j == l)
        outgoing = sum(model.y['ft', i,j] for (i,j) in model.edges if i == l)
        return incoming == outgoing
    model.cons_test = pyo.Constraint(model.nodes, rule=conservation_test)

    # no flow into sources and out of sinks
    def no_in_source_test(model, i,j):
        if j in src:
            return model.y['ft',i,j] == 0
        else:
            return pyo.Constraint.Skip
    model.no_in_source_test = pyo.Constraint(model.edges, rule=no_in_source_test)

    # nothing leaves sink
    def no_out_sink_test(model, i,j):
        if i in sink:
            return model.y['ft', i,j] == 0
        else:
            return pyo.Constraint.Skip
    model.no_out_sink_test = pyo.Constraint(model.edges, rule=no_out_sink_test)

    # If the edge is cut -> no flow
    def cut_cons_test(model, i, j):
        return model.y['ft', i, j] + model.y['d', i, j]<= model.t
    model.cut_cons_test = pyo.Constraint(model.edges, rule=cut_cons_test)

    if debug_disjointed_graph1:
        def add_cuts_graph1(model,  i, j):
            return model.y['d', i, j] == model.t
        model.add_cuts = pyo.Constraint([(1,3),(4,6)], rule=add_cuts_graph1)
    
    if debug_disjointed_graph2:
        def add_cuts_graph2(model,  i, j):
            return model.y['d', i, j] == model.t
        model.add_cuts = pyo.Constraint([(1,4)], rule=add_cuts_graph2)

    # SUBMODEL
    # Objective - Maximize the flow into the sink
    def flow_sink(model):
        return sum(model.fs[i,j] for (i, j) in model.edges if j in sink)
    model.L.o = pyo.Objective(rule=flow_sink, sense=pyo.maximize)

    # Capacity constraints
    def capacity_sys(mdl, i, j):
        return mdl.fs[i, j] <= model.t
    model.L.cap_sys = pyo.Constraint(model.L.edges, rule=capacity_sys)

    # Conservation constraints
    def conservation_sys(model, l):
        if l in sink or l in src:
            return pyo.Constraint.Skip
        incoming  = sum(model.fs[i,j] for (i,j) in model.edges if j == l)
        outgoing = sum(model.fs[i,j] for (i,j) in model.edges if i == l)
        return incoming == outgoing
    model.L.cons_sys = pyo.Constraint(model.L.nodes, rule=conservation_sys)

    # nothing enters the source
    def no_in_source(model, i,j):
        if j in src:
            return model.fs[i,j] == 0
        else:
            return pyo.Constraint.Skip
    model.L.no_in_source = pyo.Constraint(model.L.edges, rule=no_in_source)

    # nothing leaves sink
    def no_out_sink(model, i,j):
        if i in sink:
            return model.fs[i,j] == 0
        else:
            return pyo.Constraint.Skip
    model.L.no_out_sink = pyo.Constraint(model.L.edges, rule=no_out_sink)

    # nothing enters the intermediate or leaves the intermediate
    def no_in_interm(model, i,j):
        if j in inter:
            return model.fs[i,j] == 0
        else:
            return pyo.Constraint.Skip
    model.L.no_in_interm = pyo.Constraint(model.L.edges, rule=no_in_interm)

    def no_out_interm(model, i,j):
        if i in inter:
            return model.fs[i,j] == 0
        else:
            return pyo.Constraint.Skip
    model.L.no_out_interm = pyo.Constraint(model.L.edges, rule=no_out_interm)

    # Cut constraints for flow 3
    def cut_cons_sys(mdl, i, j):
        return mdl.fs[i,j] + model.y['d',i,j]<= model.t
    model.L.cut_cons_sys = pyo.Constraint(model.L.edges, rule=cut_cons_sys)

    print(" ==== Successfully added objective and constraints! ==== ")
    if debug:
        model.pprint()

    with Solver('pao.pyomo.REG') as solver:
        results = solver.solve(model, tee=True)

    # opt = pao.Solver("pao.pyomo.FA")
    # results = opt.solve(model)

    # model.pprint()
    ftest = dict()
    fsys = dict()
    d = dict()
    F = 0

    print(" ")
    print('Inverse of total flow value {0}'.format(model.t.value))

    for (i,j) in model.edges:
        F = (1.0)/(model.t.value)
        ftest.update({(i,j): model.y['ft', i,j].value*F})
        d.update({(i,j): model.y['d', i,j].value*F})
    for (i,j) in model.L.edges:
        fsys.update({(i,j): model.L.fs[i,j].value*F})

    for key in d.keys():
        print('Cut value {0} to {1} at {2}'.format(GD.node_dict[key[0]], GD.node_dict[key[1]],d[key]))
    print(" ")

    for key in ftest.keys():
        print('Flow S->T on graph with I value {0} to {1} at {2}'.format(GD.node_dict[key[0]], GD.node_dict[key[1]],ftest[key]))
    print(" ")
    for key in fsys.keys():
        print('Flow S->T on graph without I value {0} to {1} at {2}'.format(GD.node_dict[key[0]], GD.node_dict[key[1]],fsys[key]))
        print('Total byflow value {0}'.format(F))
    print(" ")

    print('Total flow value {0}'.format(F))
    st()

    return ftest, fsys, d, F

def postprocess_cuts(G, cuts, acc_test, init, node_dict, state_map):
    for cut in cuts: # remove the cuts from the graph
        print(cut)
        G.remove_edge(cut[0],cut[1])

    dead_ends = []
    for cut in cuts: # prune the trap states / dead ends
        ok = True
        for target in acc_test:
            if not nx.has_path(G,cut[0],target):
                ok = False
        if not ok:
            dead_ends.append(cut[0])
    for dead_end in dead_ends:
        in_edges = G.in_edges(dead_end)
        sys_nodes_to_prune = []
        for edge in in_edges:
            for target in acc_test:
                need_cut = False
                if nx.has_path(G, edge[0], target):
                    need_cut = True
            if need_cut:
                sys_nodes_to_prune.append(edge[0])

    new_cuts = []
    for node in sys_nodes_to_prune:
        in_edges = deepcopy(G.in_edges(node))
        for edge in in_edges:
            cut_ok = False
            for target in acc_test:
                if nx.has_path(G,edge[0],target) and nx.has_path(G,init[0],edge[0]):
                    cut_ok = True

            if cut_ok:
                G.remove_edge(edge[0],edge[1])
                new_cuts.append(edge)
    return G, new_cuts
