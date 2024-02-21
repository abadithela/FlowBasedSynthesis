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
from feasibility_constraints import add_static_obstacle_constraints_on_S, add_static_obstacle_constraints_on_G
from setup_graphs import setup_graphs_for_optimization
from initialize_max_flow import initialize_max_flow
from copy import deepcopy

debug = True
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

    src = GD.init
    sink = GD.sink
    inter = cleaned_intermed

    # 'ft': tester flow, and d: cut values
    vars = ['ft', 'd']
    model.y = pyo.Var(vars, model.edges, within=pyo.NonNegativeReals)
    model.t = pyo.Var(within=pyo.NonNegativeReals)

    # model variables for the dual
    model.l = pyo.Var(model.edges, within=pyo.NonNegativeReals)
    model.m = pyo.Var(model.nodes, within=pyo.NonNegativeReals)

    # Add constraints that system will always have a path
    # model = add_static_obstacle_constraints_on_S(model, GD, SD)
    # model = add_static_obstacle_constraints_on_G(model, GD)

    # compute max flow for lower bound on t
    f_init, _, t_lower = initialize_max_flow(G, src, inter, sink)
    if init: # initialize the flows with valid max flow
        for (i,j) in model.edges:
            model.y['d', i, j] = 0
            model.y['ft', i, j] = f_init[(i,j)]
        model.t = t_lower

    # Objective - minimize (1-gamma)*t + gamma*sum(lam*(t-de))
    def obj(model):
        gam = 0.999
        second_term = sum(model.l[i,j]*(model.t-model.y['d',i,j]) for (i, j) in model.edges)
        return (1-gam)*model.t + gam*second_term
    model.o = pyo.Objective(rule=obj, sense=pyo.minimize)

    # Constraints
    # Maximize the flow into the sink
    def flow_src_test(model):
        return 1 == sum(model.y['ft', i,j] for (i, j) in model.edges if i in src)
    model.min_constr = pyo.Constraint(rule=flow_src_test)

    # constraints on t
    model.bounded_t = pyo.ConstraintList()
    t_lower_bound = t_lower <= model.t
    model.bounded_t.add(expr = t_lower_bound)
    t_upper_bound = model.t <= 1.0
    model.bounded_t.add(expr = t_upper_bound)

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

    # constraints for inner dual problem
    # partition constraint for max flow dual
    model.max_flow_partitions = pyo.ConstraintList()
    node_list = list(G.nodes)
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
    model.max_flow_cut = pyo.Constraint(model.edges, rule=max_flow_cut)

    # no cuts on edges for intermediate nodes to get max flow
    def no_cuts_inter(model, i,j):
        if i in inter or j in inter:
            return model.l[i,j] == 0
        else:
            return pyo.Constraint.Skip
    model.no_cuts_inter = pyo.Constraint(model.edges, rule=no_cuts_inter)

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

    model.display()

    ftest = dict()
    d = dict()
    lam = dict()
    mu = dict()

    for (i,j) in model.edges:
        F = (1.0)/(model.t.value)
        ftest.update({(i,j): model.y['ft', i,j].value*F})
        d.update({(i,j): model.y['d', i,j].value*F})
        lam.update({(i,j): model.l[i,j].value})
    for k in model.nodes:
        mu.update({(k): model.m[k].value})

    for key in d.keys():
        print('{0} to {1} at {2}'.format(GD.node_dict[key[0]], GD.node_dict[key[1]],d[key]))

    st()
    return ftest, d, F
