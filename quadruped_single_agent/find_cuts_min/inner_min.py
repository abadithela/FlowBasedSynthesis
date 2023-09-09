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

def solve_inner_min(GD, SD):
    cleaned_intermed = [x for x in GD.acc_test if x not in GD.acc_sys]
    # create G and remove self-loops
    G = GD.graph
    to_remove = []
    for i, j in G.edges:
        if i == j:
            to_remove.append((i,j))
    G.remove_edges_from(to_remove)

    model = pyo.ConcreteModel()
    model.nodes = G.nodes
    model.edges = G.edges

    src = GD.init
    sink = GD.sink
    inter = cleaned_intermed

    # dummy outer player vars
    d = 0
    t = 1
    # model variables for the dual
    model.l = pyo.Var(model.edges, within=pyo.NonNegativeReals)
    model.m = pyo.Var(model.nodes, within=pyo.NonNegativeReals)

    # Objective - minimize gamma*sum(lam*(t-de))
    def obj(model):
        gam = 1
        second_term = sum(model.l[i,j]*(t-d) for (i, j) in model.edges)
        return gam*second_term
    model.o = pyo.Objective(rule=obj, sense=pyo.minimize)

    # Constraints
    # partition constraint for max flow dual
    model.max_flow_partitions = pyo.ConstraintList()
    node_list = list(G.nodes)
    for count,i in enumerate(node_list):
        for j in node_list:
            if i in src and j in sink:
                expression = model.m[i] - model.m[j] >= 1
                model.max_flow_partitions.add(expr = expression)
            elif i in sink and j in src:
                expression = model.m[j] - model.m[i] >= 1
                model.max_flow_partitions.add(expr = expression)

    # max flow cut constraint
    def max_flow_cut(model, i,j):
        expr = model.l[i,j] - model.m[i] + model.m[j] >= 0
        return expr
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

    opt = SolverFactory("gurobi", solver_io="python")
    opt.options['NonConvex'] = 2

    opt.solve(model, tee= True)

    model.display()


    lam = dict()
    mu = dict()
    F = 0

    for (i,j) in model.edges:
        lam.update({(i,j): model.l[i,j].value})
    for k in model.nodes:
        mu.update({(k): model.m[k].value})

    st()
    return lam, mu
