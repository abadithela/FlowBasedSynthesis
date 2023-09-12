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
from flow_constraints.feasibility_constraints import add_static_obstacle_constraints_on_S
# from setup_graphs import setup_graphs_for_optimization
from flow_constraints.initialize_max_flow import initialize_max_flow
from copy import deepcopy
import logging
from pyomo.util.infeasible import log_infeasible_constraints

debug = True
init = True

GAMMA = 1000

def solve_bilevel(GD, SD):
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
    S_src = SD.init
    S_sink = SD.acc_sys

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

    # Introduce SUBMODEL
    # fixed variables defined by the upper level (tester)
    fixed_variables = [model.y['d',i,j] for i,j in model.edges] # Cut edges
    fixed_variables.extend([model.y['ft',i,j] for i,j in model.edges]) # Flow 1
    fixed_variables.extend([model.t]) # 1/F
    # Submodel - variables defined by the system under test
    model.L = SubModel(fixed=fixed_variables)
    model.L.edges = model.edges
    model.L.nodes = model.nodes
    model.L.fby = pyo.Var(model.L.edges, within=pyo.NonNegativeReals) # Flow 3 (from s to t not through i)
    model.L.ts = pyo.Var(within=pyo.NonNegativeReals)

    # Add constraints that system will always have a path
    model = add_static_obstacle_constraints_on_S(model, GD, SD, init)

    # compute max flow for lower bound on t
    f_init, fby_init, t_lower, f_on_s_init = initialize_max_flow(G, src, inter, sink, S, S_src, S_sink)
    if init: # initialize the flows with valid max flow
        for (i,j) in model.edges:
            model.y['d', i, j] = 0
            model.y['ft', i, j] = f_init[(i,j)]
            model.L.fby[i, j] = fby_init[(i,j)]
        for (i,j) in model.s_edges:
            model.f_on_S[i, j] = f_on_s_init[(i,j)]
        model.t = t_lower

    # Objective - minimize 1/F + lambda*f_sys/F
    def mcf_flow(model):
        bypass_flow = sum(model.L.fby[i,j] for (i, j) in model.L.edges if i in src)
        # sum_de = sum(model.y['d', i, j] for (i,j) in model.edges)
        return model.t + GAMMA*bypass_flow# + sum_de
        # return bypass_flow
    model.o = pyo.Objective(rule=mcf_flow, sense=pyo.minimize)

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

    # SUBMODEL
    # Objective - Maximize the flow into the sink
    def flow_sink(model):
        return model.ts + GAMMA*sum(model.fby[i,j] for (i, j) in model.edges if j in sink)
    model.L.o = pyo.Objective(rule=flow_sink, sense=pyo.maximize)

    # set t equals
    model.L.equal_t = pyo.ConstraintList()
    t_equals = model.L.ts == model.t
    model.L.equal_t.add(expr = t_equals)

    # Capacity constraints
    def capacity_sys(mdl, i, j):
        return mdl.fby[i, j] <= model.t
    model.L.cap_sys = pyo.Constraint(model.L.edges, rule=capacity_sys)

    # Conservation constraints
    def conservation_sys(model, l):
        if l in sink or l in src:
            return pyo.Constraint.Skip
        incoming  = sum(model.fby[i,j] for (i,j) in model.edges if j == l)
        outgoing = sum(model.fby[i,j] for (i,j) in model.edges if i == l)
        return incoming == outgoing
    model.L.cons_sys = pyo.Constraint(model.L.nodes, rule=conservation_sys)

    # nothing enters the source
    def no_in_source(model, i,j):
        if j in src:
            return model.fby[i,j] == 0
        else:
            return pyo.Constraint.Skip
    model.L.no_in_source = pyo.Constraint(model.L.edges, rule=no_in_source)

    # nothing leaves sink
    def no_out_sink(model, i,j):
        if i in sink:
            return model.fby[i,j] == 0
        else:
            return pyo.Constraint.Skip
    model.L.no_out_sink = pyo.Constraint(model.L.edges, rule=no_out_sink)

    # nothing enters the intermediate or leaves the intermediate
    def no_in_interm(model, i,j):
        if j in inter:
            return model.fby[i,j] == 0
        else:
            return pyo.Constraint.Skip
    model.L.no_in_interm = pyo.Constraint(model.L.edges, rule=no_in_interm)

    def no_out_interm(model, i,j):
        if i in inter:
            return model.fby[i,j] == 0
        else:
            return pyo.Constraint.Skip
    model.L.no_out_interm = pyo.Constraint(model.L.edges, rule=no_out_interm)

    # Cut constraints for flow 3
    def cut_cons_sys(mdl, i, j):
        return mdl.fby[i,j] + model.y['d',i,j]<= model.t
    model.L.cut_cons_sys = pyo.Constraint(model.L.edges, rule=cut_cons_sys)

    print(" ==== Successfully added objective and constraints! ==== ")
    if debug:
        model.pprint()

    # with Solver('pao.pyomo.REG') as solver:
    #     results = solver.solve(model, tee=True)

    with Solver('pao.pyomo.REG') as solver:
        results = solver.solve(model, tee=True, max_iter=5000, warmstart=True)

    log_infeasible_constraints(model, log_expression=True, log_variables=True)
    logging.basicConfig(filename='optimization.log', encoding='utf-8', level=logging.INFO)

    # model.pprint()
    ftest = dict()
    fby = dict()
    d = dict()
    f_on_s = dict()

    for (i,j) in model.edges:
        F = (1.0)/(model.t.value)
        ftest.update({(i,j): model.y['ft', i,j].value*F})
        d.update({(i,j): model.y['d', i,j].value*F})
    for (i,j) in model.L.edges:
        fby.update({(i,j): model.L.fby[i,j].value*F})

    if debug:
        print('------- d_e -------')
        for (i,j) in model.s_edges:
            f_on_s.update({(i,j): model.f_on_S[i,j].value*F})

        for key in d.keys():
            print('{0} to {1} at {2}'.format(GD.node_dict[key[0]], GD.node_dict[key[1]],d[key]))

        print('------- f_on_s -------')
        for key in f_on_s.keys():
            print('{0} to {1} at {2}'.format(GD.node_dict[key[0]], GD.node_dict[key[1]],f_on_s[key]))
        print('------- f_by -------')
        for key in fby.keys():
            print('{0} to {1} at {2}'.format(GD.node_dict[key[0]], GD.node_dict[key[1]],fby[key]))


    print('Flow on S:')
    print(sum(f_on_s[i,j] for (i, j) in model.s_edges if i in SD.init))
    st()
    return ftest, fby, d, F, f_on_s
