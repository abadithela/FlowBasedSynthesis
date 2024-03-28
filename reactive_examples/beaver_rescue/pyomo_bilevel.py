'''
Bilevel optimization from ICRA2023 paper, only for comparison purposes.
'''
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
import time
from ipdb import set_trace as st

def find_map_G_to_S(GD,SD):
    G_truncated = {}
    S_annot = {}
    map_G_to_S = {}
    for node in GD.node_dict:
        G_truncated.update({node: GD.node_dict[node][0]})
    for node in SD.node_dict:
        S_annot.update({node: SD.node_dict[node][0]})
    for node in G_truncated:
        for sys_node in S_annot:
            if G_truncated[node]  == S_annot[sys_node]:
                map_G_to_S.update({node: sys_node})

    return map_G_to_S

def solve_bilevel(GD, SD):
    nodes = GD.nodes
    edges = GD.edges
    init = GD.init
    intermed = [int for int in GD.int if int not in GD.sink]
    goal = GD.sink

    # map_G_to_S = find_map_G_to_S(GD,SD)
    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    # remove self loops
    for i,j in edges:
        if i == j:
            G.remove_edge(i,j)

    model = pyo.ConcreteModel()
    model.name = 'virtual_gg'
    model.nodes = list(G.nodes())
    model.edges = list(G.edges())

    src = init # list
    sink = goal # list
    int = intermed # list
    vars = ['f1_e', 'f2_e', 'd_e', 'F']
    model.y = pyo.Var(vars, model.edges, within=pyo.NonNegativeReals)
    model.t = pyo.Var(within=pyo.NonNegativeReals)

    # Introduce SUBMODEL
    # fixed variables defined by the upper level (tester)
    fixed_variables = [model.y['d_e',i,j] for i,j in model.edges] # Cut edges
    fixed_variables.extend([model.y['f1_e',i,j] for i,j in model.edges]) # Flow 1
    fixed_variables.extend([model.y['f2_e',i,j] for i,j in model.edges]) # Flow 2
    # fixed_variables.extend([model.y['F',i,j] for i,j in model.edges]) # total flow through i
    fixed_variables.extend([model.t]) # 1/F
    # Submodel - variables defined by the system under test
    model.L = SubModel(fixed=fixed_variables)
    model.L.edges = model.edges
    model.L.nodes = model.nodes
    model.L.f3 = pyo.Var(model.L.edges, within=pyo.NonNegativeReals) # Flow 3 (from s to t not through i)

    # Upper level Objective

    # Objective - minimize 1/F + lambda*f_3/F
    def mcf_flow(model):
        lam = 1000
        flow_3 = sum(model.L.f3[i,j] for (i, j) in model.L.edges if j in sink)
        return (model.t + lam * flow_3)
    model.o = pyo.Objective(rule=mcf_flow, sense=pyo.minimize)

    # Constraints
    # Maximize the flow into the sink
    def flow_src1(model):
        return 1 <= sum(model.y['f1_e', i,j] for (i, j) in model.edges if i in src)
    def flow_src2(model):
        return 1 <= sum(model.y['f2_e', i,j] for (i, j) in model.edges if i in int)
    model.min_constr1 = pyo.Constraint(rule=flow_src1)
    model.min_constr2 = pyo.Constraint(rule=flow_src2)

    def capacity1(model, i, j):
        return model.y['f1_e', i, j] <= model.t
    def capacity2(model, i, j):
        return model.y['f2_e', i, j] <= model.t
    model.cap1 = pyo.Constraint(model.edges, rule=capacity1)
    model.cap2 = pyo.Constraint(model.edges, rule=capacity2)

    # conservation constraints
    def conservation1(model, k):
        if k in src or k in int:
            return pyo.Constraint.Skip
        incoming  = sum(model.y['f1_e', i, j] for (i, j) in model.edges if j == k)
        outgoing = sum(model.y['f1_e',i,j] for (i, j) in model.edges if i == k)
        return incoming == outgoing
    model.cons1 = pyo.Constraint(model.nodes, rule=conservation1)

    def conservation2(model, k):
        if k in int or k in sink:
            return pyo.Constraint.Skip
        incoming  = sum(model.y['f2_e', i,j] for (i,j) in model.edges if j == k)
        outgoing = sum(model.y['f2_e', i,j] for (i,j) in model.edges if i == k)
        return incoming == outgoing
    model.cons2 = pyo.Constraint(model.nodes, rule=conservation2)

    # no flow into sources and out of sinks
    def no_in_source1(model, i,k):
        if k in src:
            return model.y['f1_e',i,k] == 0
        else:
            return pyo.Constraint.Skip
    model.no_in_source1 = pyo.Constraint(model.edges, rule=no_in_source1)
    # nothing leaves sink
    def no_out_sink1(model, i,k):
        if i in int:
            return model.y['f1_e', i,k] == 0
        else:
            return pyo.Constraint.Skip
    model.no_out_sink1 = pyo.Constraint(model.edges, rule=no_out_sink1)
    # =================================================================== #
    def no_in_source2(model, i,k):
        if k in int:
            return model.y['f2_e',i,k] == 0
        else:
            return pyo.Constraint.Skip
    model.no_in_source2 = pyo.Constraint(model.edges, rule=no_in_source2)

    # nothing leaves sink
    def no_out_sink2(model, i,k):
        if i in sink:
            return model.y['f2_e',i,k] == 0
        else:
            return pyo.Constraint.Skip
    model.no_out_sink2 = pyo.Constraint(model.edges, rule=no_out_sink2)
    # =================================================================== #

    # If the edge is cut -> no flow
    def cut_cons1(model, i, j):
        return model.y['f1_e',i,j] + model.y['d_e',i,j]<= model.t
    model.cut_cons1 = pyo.Constraint(model.edges, rule=cut_cons1)

    def cut_cons2(model, i, j):
        return model.y['f2_e',i,j] + model.y['d_e',i,j]<= model.t
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
    def conservation(model, k):
        if k in sink or k in src:
            return pyo.Constraint.Skip
        incoming  = sum(model.f3[i,j] for (i,j) in model.edges if j == k)
        outgoing = sum(model.f3[i,j] for (i,j) in model.edges if i == k)
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
        if j in int:
            return model.f3[i,j] == 0
        else:
            return pyo.Constraint.Skip
    model.L.no_in_interm = pyo.Constraint(model.L.edges, rule=no_in_interm)

    def no_out_interm(model, i,j):
        if j in int:
            return model.f3[i,j] == 0
        else:
            return pyo.Constraint.Skip
    model.L.no_out_interm = pyo.Constraint(model.L.edges, rule=no_out_interm)

    # Cut constraints for flow 3
    def cut_cons(mdl, i, j):
        return mdl.f3[i,j] + model.y['d_e',i,j]<= model.t
    model.L.cut_cons = pyo.Constraint(model.L.edges, rule=cut_cons)

    # Add constraints that system will always have a path
    model = add_feasibility_constraints(model, GD, SD)

    print(" ==== Successfully added objective and constraints! ==== ")

    solver = Solver('pao.pyomo.REG')
    ti = time.time()
    results = solver.solve(model, tee=False)
    tf = time.time()

    bilevel_runtime = tf-ti

    f1_e = dict()
    f2_e = dict()
    f3_e = dict()
    d_e = dict()

    for (i,j) in model.edges:
        F = 1/model.t.value
        f1_e.update({((i,j)): model.y['f1_e', i,j].value*F})
        f2_e.update({((i,j)): model.y['f2_e', i,j].value*F})
        d_e.update({((i,j)): model.y['d_e', i,j].value*F})
    for (i,j)in model.L.edges:
        f3_e.update({((i,j)): model.L.f3[i,j].value*F})

    for key in d_e.keys():
        if d_e[key] > 0.9:
            print('{0} to {1} at {2}'.format(GD.node_dict[key[0]], GD.node_dict[key[1]],d_e[key]))


    return f1_e, f2_e, f3_e, d_e, F, bilevel_runtime


def add_feasibility_constraints(model, GD, SD):
    '''
    Remember the history variable and check all cuts for that q.
    '''
    S = nx.DiGraph()
    S.add_nodes_from(SD.nodes)
    S.add_edges_from(SD.edges)
    # remove self loops
    for i,j in SD.edges:
        if i == j:
            S.remove_edge(i,j)

    map_G_to_S = find_map_G_to_S(GD,SD)

    node_list = []
    for node in GD.nodes:
        node_list.append(GD.node_dict[node])

    qs = list(set([node[-1] for node in node_list]))
    vars = ['fS_'+ str(q) for q in qs]

    src = SD.init
    sink = SD.acc_sys

    model.s_edges = S.edges
    model.s_nodes = S.nodes
    model.s_var = pyo.Var(vars, model.s_edges, within=pyo.NonNegativeReals)

    # feasibility constraint list
    model.feasibility = pyo.ConstraintList()


    for q in qs:
        # Match the edge cuts from G to S
        for (i,j) in model.edges:
            if GD.node_dict[i][-1] == q:
                imap = map_G_to_S[i]
                jmap = map_G_to_S[j]
                expression =  model.s_var['fS_'+ str(q), imap, jmap] + model.y['d_e', i, j] <= model.t
                model.feasibility.add(expr = expression)

        # Normal flow constraints
        # Preserve flow of 1 in S
        expression =  model.t <= sum(model.s_var['fS_'+ str(q), i,j] for (i, j) in model.s_edges if i in src)
        model.feasibility.add(expr = expression)

        # Capacity constraint on flow
        for (i,j) in model.s_edges:
            expression =  model.s_var['fS_'+ str(q),  i, j] <= model.t
            model.feasibility.add(expr = expression)

        # Conservation constraints:
        for k in model.s_nodes:
            if k not in src and k not in sink:
                incoming  = sum(model.s_var['fS_'+ str(q),i,j] for (i,j) in model.s_edges if (j == k))
                outgoing = sum(model.s_var['fS_'+ str(q), i,j] for (i,j) in model.s_edges if (i == k))
                expression = incoming == outgoing
                model.feasibility.add(expr = expression)

        # no flow into sources and out of sinks
        for (i,j) in model.s_edges:
            if j in src:
                expression = model.s_var['fS_'+ str(q),i,j] == 0
                model.feasibility.add(expr = expression)

        # nothing leaves sink
        for (i,j) in model.s_edges:
            if i in sink:
                expression = model.s_var['fS_'+ str(q),i,k] == 0
                model.feasibility.add(expr = expression)

    return model
