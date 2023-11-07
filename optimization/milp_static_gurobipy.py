'''
Gurobipy implementation of the MILP for static obstacles - using the callback
function to terminate of the objective has not improved in 30s.
'''

import gurobipy as gp
from gurobipy import GRB
import time
import numpy as np
from ipdb import set_trace as st
import networkx as nx
from optimization.feasibility_constraints import find_map_G_S
from gurobipy import *
from copy import deepcopy

# Callback function
def cb(model, where):
    if where == GRB.Callback.MIPNODE:
        # Get model objective
        obj = model.cbGet(GRB.Callback.MIPNODE_OBJBST)

        # Has objective changed?
        if abs(obj - model._cur_obj) > 1e-8:
            # If so, update incumbent and time
            model._cur_obj = obj
            model._time = time.time()

    # Terminate if objective has not improved in 30s
    if time.time() - model._time > 30:
        model.terminate()

# Gurobi implementation
def solve_max_gurobi(GD, SD):
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

    model_edges = list(G.edges)
    model_nodes = list(G.nodes)
    model_edges_without_I = list(G_minus_I.edges)
    model_nodes_without_I = list(G_minus_I.nodes)

    src = GD.init
    sink = GD.sink
    inter = cleaned_intermed

    # for the flow on S
    map_G_to_S = find_map_G_S(GD,SD)

    s_sink = SD.acc_sys
    s_src = SD.init[0]

    model_s_edges = list(S.edges)
    model_s_nodes = list(S.nodes)

    model = Model()
    # add variables
    # outer player
    f = model.addVars(model_edges, name="flow")
    d_aux = model.addVars(model_edges, name="d_aux")
    # inner player
    d = model.addVars(model_edges_without_I, vtype=GRB.BINARY, name="d") # Binary variable
    m = model.addVars(model_nodes_without_I, name="m")

    # Define Objective
    term = sum(f[i,j] for (i, j) in model_edges if i in src)
    ncuts = sum(d_aux[i,j] for (i, j) in model_edges)
    model.setObjective(term - 10e-3*ncuts, GRB.MAXIMIZE)

    # Nonnegativity - lower bounds
    model.addConstrs((d[i, j] >= 0 for (i,j) in model_edges_without_I), name='d_nonneg')
    model.addConstrs((m[i] >= 0 for i in model_nodes_without_I), name='mu_nonneg')
    model.addConstrs((f[i, j] >= 0 for (i,j) in model_edges), name='f_nonneg')
    model.addConstrs((d_aux[i, j] >= 0 for (i,j) in model_edges), name='d_aux_nonneg')

    # upper bounds
    model.addConstrs((d[i, j] <= 1 for (i,j) in model_edges_without_I), name='d_upper_b')
    model.addConstrs((m[i] <= 1 for i in model_nodes_without_I), name='mu_upper_b')
    model.addConstrs((d_aux[i, j] <= 1 for (i,j) in model_edges), name='d_aux_upper_b')
    # capacity (upper bound for f)
    model.addConstrs((f[i, j] <= 1 for (i,j) in model_edges), name='capacity')

    # preserve flow
    model.addConstr((1 <= sum(f[i,j] for (i, j) in model_edges if i in src)), name='conserve_F')

    # conservation
    model.addConstrs((sum(f[i,j] for (i,j) in model_edges if j == l) == sum(f[i,j] for (i,j) in model_edges if i == l) for l in model_nodes if l not in src and l not in sink), name='conservation')

    # no in source or out of sink
    model.addConstrs((f[i,j] == 0 for (i,j) in model_edges if j in src or i in sink), name="no_out_sink_in_src")

    # cut constraint
    model.addConstrs((f[i,j] + d_aux[i,j] <= 1 for (i,j) in model_edges), name='cut_cons')

    # map d to d_aux
    model.addConstrs((d[i,j] == d_aux[i,j] for (i,j) in model_edges_without_I), name='match_d_to_all_edges')

    # source sink partitions
    for i in model_nodes_without_I:
        for j in model_nodes_without_I:
            if i in src and j in sink:
                model.addConstr(m[i] - m[j] >= 1)

    # max flow cut constraint
    model.addConstrs((d[i,j] - m[i] + m[j] >= 0 for (i,j) in model_edges_without_I))


    # --------- add feasibility constraints to preserve flow f_s on S
    f_s = model.addVars(model_s_edges, name="flow_on_S")

    # nonnegativitiy for f_s (lower bound)
    model.addConstrs((f_s[i, j] >= 0 for (i,j) in model_s_edges), name='f_s_nonneg')

    # capacity on S (upper bound on f_s)
    model.addConstrs((f_s[i, j] <= 1 for (i,j) in model_s_edges), name='capacity_f_S')

    # Match the edge cuts from G to S
    for (i,j) in model_edges:
        imap = map_G_to_S[i]
        jmap = map_G_to_S[j]
        model.addConstr(f_s[imap, jmap] + d_aux[i, j] <= 1)

    # Preserve flow of 1 in S
    model.addConstr((1 <= sum(f_s[i,j] for (i, j) in model_s_edges if i == s_src)), name='conserve_F_on_S')

    # conservation on S
    model.addConstrs((sum(f_s[i,j] for (i,j) in model_s_edges if j == l) == sum(f_s[i,j] for (i,j) in model_s_edges if i == l) for l in model_s_nodes if l != s_src and l not in s_sink), name='conservation_f_S')

    # no flow into sources and out of sinks on S
    model.addConstrs((f_s[i,j] == 0 for (i,j) in model_s_edges if j == s_src or i in s_sink), name="no_out_sink_in_src_on_S")


    # --------- map static obstacles to other edges in G
    # model = map_static_obstacles_to_G(model, GD)
    for count, (i,j) in enumerate(model_edges):
        out_state = GD.node_dict[i][0]
        in_state = GD.node_dict[j][0]
        for (imap,jmap) in model_edges[count+1:]:
            if out_state == GD.node_dict[imap][0] and in_state == GD.node_dict[jmap][0]:
                model.addConstr(d_aux[i, j] == d_aux[imap, jmap])


    # ---------  add bidirectional cuts on G
    # model = add_bidirectional_edge_cuts_on_G(model, GD)
    for count, (i,j) in enumerate(model_edges):
        out_state = GD.node_dict[i][0]
        in_state = GD.node_dict[j][0]
        for (imap,jmap) in model_edges[count+1:]:
            if in_state == GD.node_dict[imap][0] and out_state == GD.node_dict[jmap][0]:
                model.addConstr(d_aux[i, j] == d_aux[imap, jmap])


    # --------- set parameters
    # Last updated objective and time (for callback function)
    model._cur_obj = float('inf')
    model._time = time.time()
    model.Params.Seed = np.random.randint(0,100)

    # model.Params.InfUnbdInfo = 1

    # optimize
    model.optimize(callback=cb)

    if model.status == 4:
        model.Params.DualReductions = 0
        model.optimize(callback=cb)

        exit_status = 'inf'

        return exit_status, [], [], None

    else:
        # --------- parse output
        d_vals = dict()
        f_vals = dict()

        for (i,j) in model_edges:
            f_vals.update({(i,j): f[i,j].X})
        for (i,j) in model_edges_without_I:
            d_vals.update({(i,j): d[i,j].X})

        flow = sum(f[i,j].X for (i,j) in model_edges if i in src)

        for key in d_vals.keys():
            if d_vals[key] > 0.9:
                print('{0} to {1} at {2}'.format(GD.node_dict[key[0]], GD.node_dict[key[1]],d_vals[key]))

        exit_status = 'opt'

        return exit_status, f_vals, d_vals, flow
