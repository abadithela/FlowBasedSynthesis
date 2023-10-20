# Solve the bilevel optimization as LFP (Linear Fractional Program) to
# route the flow through the vertices satisfying the test specification
# J. Graebener, A. Badithela
# Setting lambda*t = de sets the zero bypass flow as a condition. Get a single MILP 
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

def solve_min(GD, SD, return_lam=False):
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
    vars = ['f', 'd']
    model.y = pyo.Var(vars, model.edges, within=pyo.NonNegativeReals)
    model.t = pyo.Var(within=pyo.NonNegativeReals)

    # model variables for the dual
    model.l = pyo.Var(model.edges_without_I, within=pyo.Binary)
    model.m = pyo.Var(model.nodes_without_I, within=pyo.NonNegativeReals)

    # Add constraints that system will always have a path
    model = add_feasibility_constraints(model, GD, SD)

    # compute max flow for lower bound on t
    f_init, _, t_lower = initialize_max_flow(G, src, inter, sink)
    if init: # initialize the flows with valid max flow
        for (i,j) in model.edges:
            model.y['d', i, j] = 0
            model.y['f', i, j] = f_init[(i,j)]
        model.t = t_lower

    # Objective - minimize (1-gamma)*t + gamma*sum(lam*(t-de))
    def obj(model):
        # second_term = sum(model.l[i,j]*(model.t-model.y['d',i,j]) for (i, j) in model.edges_without_I)
        third_term = sum(model.y['d',i,j] for (i, j) in model.edges)
        return model.t + 10e-3*third_term
    model.o = pyo.Objective(rule=obj, sense=pyo.minimize)

    # Constraints
    # coupled constraint that gives zero bypass flow
    def zero_bypass(model, i, j):
        return model.l[i,j]*model.t ==  model.y['d',i,j]
    model.zero_bypass = pyo.Constraint(model.edges_without_I, rule=zero_bypass)

    # Maximize the flow into the sink
    def flow_src_test(model):
        return 1 == sum(model.y['f', i,j] for (i, j) in model.edges if i in src)
    model.min_constr = pyo.Constraint(rule=flow_src_test)

    # constraints on t
    model.bounded_t = pyo.ConstraintList()
    t_lower_bound = t_lower <= model.t
    model.bounded_t.add(expr = t_lower_bound)
    t_upper_bound = model.t <= 1.0
    model.bounded_t.add(expr = t_upper_bound)

    def capacity_test(model, i, j):
        return model.y['f',i, j] <= model.t
    model.cap_test = pyo.Constraint(model.edges, rule=capacity_test)

    # conservation constraints
    def conservation_test(model, l):
        if l in src or l in sink:
            return pyo.Constraint.Skip
        incoming  = sum(model.y['f', i,j] for (i,j) in model.edges if j == l)
        outgoing = sum(model.y['f', i,j] for (i,j) in model.edges if i == l)
        return incoming == outgoing
    model.cons_test = pyo.Constraint(model.nodes, rule=conservation_test)

    # no flow into sources and out of sinks
    def no_in_source_test(model, i,j):
        if j in src:
            return model.y['f',i,j] == 0
        else:
            return pyo.Constraint.Skip
    model.no_in_source_test = pyo.Constraint(model.edges, rule=no_in_source_test)

    # nothing leaves sink
    def no_out_sink_test(model, i,j):
        if i in sink:
            return model.y['f', i,j] == 0
        else:
            return pyo.Constraint.Skip
    model.no_out_sink_test = pyo.Constraint(model.edges, rule=no_out_sink_test)

    # If the edge is cut -> no flow
    def cut_cons_test(model, i, j):
        return model.y['f', i, j] + model.y['d', i, j]<= model.t
    model.cut_cons_test = pyo.Constraint(model.edges, rule=cut_cons_test)

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
        return model.l[i,j] - model.m[i] + model.m[j] >= 0
    model.max_flow_cut = pyo.Constraint(model.edges_without_I, rule=max_flow_cut)

    print(" ==== Successfully added objective and constraints! ==== ")
    if debug:
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
    lam = dict()
    mu = dict()

    for (i,j) in model.edges:
        F = (1.0)/(model.t.value)
        ftest.update({(i,j): model.y['f', i,j].value*F})
        d.update({(i,j): model.y['d', i,j].value*F})
    for (i,j) in model.edges_without_I:
        lam.update({(i,j): model.l[i,j].value})
    for k in model.nodes_without_I:
        mu.update({(k): model.m[k].value})

    for key in d.keys():
        print('{0} to {1} at {2}'.format(GD.node_dict[key[0]], GD.node_dict[key[1]],d[key]))

    # st()
    if return_lam:
        return ftest, d, F, lam, mu
    return ftest, d, F

def solve_max(GD, SD, return_lam=False):
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
    vars = ['f', 'd']
    model.y = pyo.Var(vars, model.edges, within=pyo.NonNegativeReals)
    model.t = pyo.Var(within=pyo.NonNegativeReals)

    # model variables for the dual
    model.l = pyo.Var(model.edges_without_I, within=pyo.Binary)
    model.m = pyo.Var(model.nodes_without_I, within=pyo.NonNegativeReals)

    model.a = pyo.Var(within=pyo.NonNegativeReals)
    model.z = pyo.Var(model.edges_without_I, within=pyo.NonNegativeReals)

    # Add constraints that system will always have a path
    # model = add_feasibility_constraints(model, GD, SD)

    # compute max flow for lower bound on t
    f_init, _, t_lower = initialize_max_flow(G, src, inter, sink)
    if init: # initialize the flows with valid max flow
        for (i,j) in model.edges:
            model.y['d', i, j] = 0
            model.y['f', i, j] = f_init[(i,j)]
        model.t = t_lower

    # Objective - minimize (1-gamma)*t + gamma*sum(lam*(t-de))
    def obj(model):
        # second_term = sum(model.l[i,j]*(model.t-model.y['d',i,j]) for (i, j) in model.edges_without_I)
        third_term = sum(model.y['d',i,j] for (i, j) in model.edges)
        return model.t + 10e-3*third_term
    model.o = pyo.Objective(rule=obj, sense=pyo.minimize)

    # Constraints
    # coupled constraint that gives zero bypass flow
    def zero_bypass(model, i, j):
        return model.l[i,j]*model.t ==  model.y['d',i,j]
    model.zero_bypass = pyo.Constraint(model.edges_without_I, rule=zero_bypass)

    # bigM
    def bigM_0(model, i, j):
        return 0 <= model.z[i, j]
    model.bigM_0 = pyo.Constraint(model.edges_without_I, rule=bigM_0)

    def bigM_1(model, i, j):
        return model.z[i, j] <= model.l[i,j]
    model.bigM_1 = pyo.Constraint(model.edges_without_I, rule=bigM_1)

    def bigM_2(model, i, j):
        return model.l[i,j]-1 <= model.z[i,j]-(model.t-model.y['d',i,j])
    model.bigM_2 = pyo.Constraint(model.edges_without_I, rule=bigM_2)

    # Maximize the flow into the sink
    def flow_src_test(model):
        return 1 == sum(model.y['f', i,j] for (i, j) in model.edges if i in src)
    model.min_constr = pyo.Constraint(rule=flow_src_test)

    # constraints on t
    model.bounded_t = pyo.ConstraintList()
    t_lower_bound = t_lower <= model.t
    model.bounded_t.add(expr = t_lower_bound)
    t_upper_bound = model.t <= 1.0
    model.bounded_t.add(expr = t_upper_bound)

    def capacity_test(model, i, j):
        return model.y['f',i, j] <= model.t
    model.cap_test = pyo.Constraint(model.edges, rule=capacity_test)

    # conservation constraints
    def conservation_test(model, l):
        if l in src or l in sink:
            return pyo.Constraint.Skip
        incoming  = sum(model.y['f', i,j] for (i,j) in model.edges if j == l)
        outgoing = sum(model.y['f', i,j] for (i,j) in model.edges if i == l)
        return incoming == outgoing
    model.cons_test = pyo.Constraint(model.nodes, rule=conservation_test)

    # no flow into sources and out of sinks
    def no_in_source_test(model, i,j):
        if j in src:
            return model.y['f',i,j] == 0
        else:
            return pyo.Constraint.Skip
    model.no_in_source_test = pyo.Constraint(model.edges, rule=no_in_source_test)

    # nothing leaves sink
    def no_out_sink_test(model, i,j):
        if i in sink:
            return model.y['f', i,j] == 0
        else:
            return pyo.Constraint.Skip
    model.no_out_sink_test = pyo.Constraint(model.edges, rule=no_out_sink_test)

    # If the edge is cut -> no flow
    def cut_cons_test(model, i, j):
        return model.y['f', i, j] + model.y['d', i, j]<= model.t
    model.cut_cons_test = pyo.Constraint(model.edges, rule=cut_cons_test)

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
        return model.l[i,j] - model.m[i] + model.m[j] >= 0
    model.max_flow_cut = pyo.Constraint(model.edges_without_I, rule=max_flow_cut)

    print(" ==== Successfully added objective and constraints! ==== ")
    if debug:
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
    lam = dict()
    mu = dict()

    for (i,j) in model.edges:
        F = (1.0)/(model.t.value)
        ftest.update({(i,j): model.y['f', i,j].value*F})
        d.update({(i,j): model.y['d', i,j].value*F})
    for (i,j) in model.edges_without_I:
        lam.update({(i,j): model.l[i,j].value})
    for k in model.nodes_without_I:
        mu.update({(k): model.m[k].value})

    for key in d.keys():
        print('{0} to {1} at {2}'.format(GD.node_dict[key[0]], GD.node_dict[key[1]],d[key]))

    # st()
    if return_lam:
        return ftest, d, F, lam, mu
    return ftest, d, F
