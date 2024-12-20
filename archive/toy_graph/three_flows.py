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

debug_disjointed_graph1 = False
debug_disjointed_graph2 = True
debug = True
def solve_bilevel(GD):
# st()
    cleaned_intermed = [x for x in GD.acc_test if x not in GD.acc_sys]
    G = GD.graph

    model = pao.mpr.LinearMultilevelProblem()
    model = pyo.ConcreteModel()
    model.nodes = G.nodes
    model.edges = G.edges
    ne = len(model.edges)

    src = GD.init
    sink = GD.sink
    inter = cleaned_intermed

    vars = ['f1_e', 'f2_e', 'd_e']
    model.y = pyo.Var(vars, model.edges, within=pyo.NonNegativeReals)
    model.t = pyo.Var(within=pyo.NonNegativeReals)

    # Introduce SUBMODEL
    # fixed variables defined by the upper level (tester)
    fixed_variables = [model.y['d_e',i,j] for i,j in model.edges] # Cut edges
    fixed_variables.extend([model.y['f1_e',i,j] for i,j in model.edges]) # Flow 1
    fixed_variables.extend([model.y['f2_e',i,j] for i,j in model.edges]) # Flow 2
    fixed_variables.extend([model.t]) # 1/F
    # Submodel - variables defined by the system under test
    model.L = SubModel(fixed=fixed_variables)
    model.L.edges = model.edges
    model.L.nodes = model.nodes
    model.L.f3 = pyo.Var(model.L.edges, within=pyo.NonNegativeReals) # Flow 3 (from s to t not through i)

    # Add constraints that system will always have a path
    # model = add_feasibility_constraints(model, GD, SD)
    # model = add_static_obstacle_constraints(model, GD)

    # Objective - minimize 1/F + lambda*f_3/F
    def mcf_flow(model):
        lam = 1
        flow_3 = sum(model.L.f3[i,j] for (i, j) in model.L.edges if i in src)
        cut_value = sum(model.y['d_e', i,j] for (i, j) in model.edges)
        return model.t + ne*flow_3 + cut_value


    model.o = pyo.Objective(rule=mcf_flow, sense=pyo.minimize)

    # Constraints
    # Maximize the flow into the sink
    def flow_src1(model):
        return 1 <= sum(model.y['f1_e', i,j] for (i, j) in model.edges if i in src)
    def flow_src2(model):
        return 1 <= sum(model.y['f2_e', i,j] for (i, j) in model.edges if i in inter)
    model.min_constr1 = pyo.Constraint(rule=flow_src1)
    model.min_constr2 = pyo.Constraint(rule=flow_src2)

    def capacity1(model, i, j):
        return model.y['f1_e',i, j] <= model.t
    def capacity2(model, i, j):
        return model.y['f2_e', i, j] <= model.t
    model.cap1 = pyo.Constraint(model.edges, rule=capacity1)
    model.cap2 = pyo.Constraint(model.edges, rule=capacity2)

    # conservation constraints
    def conservation1(model, l):
        if l in src or l in inter:
            return pyo.Constraint.Skip
        incoming  = sum(model.y['f1_e', i,j] for (i,j) in model.edges if j == l)
        outgoing = sum(model.y['f1_e',i,j] for (i,j) in model.edges if i == l)
        return incoming == outgoing
    model.cons1 = pyo.Constraint(model.nodes, rule=conservation1)

    def conservation2(model, l):
        if l in inter or l in sink:
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
        if i in inter:
            return model.y['f1_e', i,j] == 0
        else:
            return pyo.Constraint.Skip
    model.no_out_sink1 = pyo.Constraint(model.edges, rule=no_out_sink1)
    # =================================================================== #
    def no_in_source2(model, i,j):
        if j in inter:
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

    if debug_disjointed_graph1:
        def add_cuts(model,  i, j):
            return model.y['d_e', i, j] == model.t
        model.add_cuts = pyo.Constraint([(1,3),(4,6)], rule=add_cuts)
    
    if debug_disjointed_graph2:
        def add_cuts(model,  i, j):
            return model.y['d_e', i, j] == model.t
        model.add_cuts = pyo.Constraint([(1,4)], rule=add_cuts)

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
    model.L.con = pyo.Constraint(model.L.nodes, rule=conservation)

    # nothing enters the source
    def no_in_source(model, i,j):
        if j in src:
            return model.f3[i,j] == 0
        else:
            return pyo.Constraint.Skip
    model.L.no_in_source = pyo.Constraint(model.L.edges, rule=no_in_source)

    # nothing leaves sink
    def no_out_sink(model, i,j):
        if i in sink:
            return model.f3[i,j] == 0
        else:
            return pyo.Constraint.Skip
    model.L.no_out_sink = pyo.Constraint(model.L.edges, rule=no_out_sink)

    # nothing enters the intermediate or leaves the intermediate
    def no_in_interm(model, i,j):
        if j in inter:
            return model.f3[i,j] == 0
        else:
            return pyo.Constraint.Skip
    model.L.no_in_interm = pyo.Constraint(model.L.edges, rule=no_in_interm)

    def no_out_interm(model, i,j):
        if i in inter:
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

    with Solver('pao.pyomo.REG') as solver:
        results = solver.solve(model, tee=True)
    
    # opt = pao.Solver("pao.mpr.REG")
    # opt = pao.Solver("pao.pyomo.FA")
    # results = opt.solve(model)

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

    # print(d_e)
    # print(F)
    for key in d_e.keys():
        print('Cut value {0} to {1} at {2}'.format(GD.node_dict[key[0]], GD.node_dict[key[1]],d_e[key]))
    print(" ")

    for key in f1_e.keys():
        print('Flow S->I value {0} to {1} at {2}'.format(GD.node_dict[key[0]], GD.node_dict[key[1]],f1_e[key]))
    print(" ")
    for key in f2_e.keys():
        print('Flow I->T value {0} to {1} at {2}'.format(GD.node_dict[key[0]], GD.node_dict[key[1]],f2_e[key]))
    print(" ")

    print('Total flow value {0}'.format(F))
    st()
    return f1_e, f2_e, f3_e, d_e, F

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
