# Gurobi Implementation
import sys
sys.path.append('..')
import numpy as np
from ipdb import set_trace as st
import networkx as nx
# from feasibility_constraints import add_static_obstacle_constraints_on_S, add_static_obstacle_constraints_on_G
from setup_graphs import setup_graphs_for_optimization
# from initialize_max_flow import initialize_max_flow
from gurobipy import *


def solve_min_gurobi(GD, SD):
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

    model_edges = list(G.edges)
    model_nodes = list(G.nodes)

    src = GD.init
    sink = GD.sink
    inter = cleaned_intermed

    model = Model()
    # add variables
    # outer player
    f = model.addVars(model_edges, name="flow")
    d = model.addVars(model_edges, name="d")
    t = model.addVar(name="t")
    # inner player
    l = model.addVars(model_edges, vtype=GRB.BINARY, name="l") # Binary variable
    m = model.addVars(model_nodes, name="m")

    # define Objective
    # Build objective function
    gam = 0.999
    # st()
    second_term = sum(l[i,j]*(t-d[i,j]) for (i, j) in model_edges)
    model.setObjective((1-gam)*t + gam*second_term, GRB.MINIMIZE)
    # model.setObjective(t + gam*second_term, GRB.MINIMIZE)

    # Nonnegativity
    model.addConstrs((l[i, j] >= 0 for (i,j) in model_edges), name='lam_nonneg')
    model.addConstrs((m[i] >= 0 for i in model_nodes), name='mu_nonneg')
    model.addConstrs((d[i, j] >= 0 for (i,j) in model_edges), name='d_nonneg')
    model.addConstrs((f[i, j] >= 0 for (i,j) in model_edges), name='f_nonneg')
    model.addConstr((t >= 0), name='t_nonneg')

    # upper bound
    model.addConstrs((l[i, j] <= 1 for (i,j) in model_edges), name='lam_upper_b')
    model.addConstrs((m[i] <= 1 for i in model_nodes), name='mu_upper_b')

    # outer player
    model.addConstr((1 == sum(f[i,j] for (i, j) in model_edges if i in src)), name='conserve_F')

    # bounded t
    model.addConstr((t <= 1.0), name='t_upper_bound')

    # capacity
    model.addConstrs((f[i, j] <= t for (i,j) in model_edges), name='capacity')

    # conservation
    model.addConstrs((sum(f[i,j] for (i,j) in model_edges if j == l) == sum(f[i,j] for (i,j) in model_edges if i == l) for l in model_nodes if l not in src and l not in sink), name='conservation')

    # no in source or out of sink
    model.addConstrs((f[i,j] == 0 for (i,j) in model_edges if j in src or i in sink), name="no_out_sink_in_src")

    # cut constraint
    model.addConstrs((f[i,j] + d[i,j] <= t for (i,j) in model_edges), name='cut_cons')

    # inner player constraints
    # source sink partitions
    for i in model_nodes:
        for j in model_nodes:
            if i in src and j in sink:
                model.addConstr(m[i] - m[j] >= 1)

    # max flow cut constraint
    model.addConstrs((l[i,j] - m[i] + m[j] >= 0 for (i,j) in model_edges))

    # no cuts on edges for intermediate nodes to get max flow
    model.addConstrs((l[i,j] == 0 for (i,j) in model_edges if i in inter or j in inter), name="no_inter")

    # set parameters
    model.params.NonConvex=2
    model.optimize()

    st()

    # st()
    d_vals = dict()
    f_vals = dict()

    for (i,j) in model_edges:
        F = (1.0)/(t.X)
        f_vals.update({(i,j): f[i,j].X*F})
        d_vals.update({(i,j): d[i,j].X*F})

    for key in d_vals.keys():
        print('{0} to {1} at {2}'.format(GD.node_dict[key[0]], GD.node_dict[key[1]],d_vals[key]))


    return d_vals, f_vals, F
