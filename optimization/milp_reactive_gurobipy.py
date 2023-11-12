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
    if time.time() - model._time > 30:# and model.SolCount >= 1:
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
    # s_src = SD.init[0]

    model_s_edges = list(S.edges)
    model_s_nodes = list(S.nodes)

    model = Model()
    # add variables
    # outer player
    f = model.addVars(model_edges, name="flow")
    # d_aux = model.addVars(model_edges, name="d_aux")
    # inner player
    d = model.addVars(model_edges_without_I, vtype=GRB.BINARY, name="d") # Binary variable
    m = model.addVars(model_nodes_without_I, name="m")

    # Define Objective
    term = sum(f[i,j] for (i, j) in model_edges if i in src)
    ncuts = sum(d[i,j] for (i, j) in model_edges_without_I)
    model.setObjective(term - 10e-3*ncuts, GRB.MAXIMIZE)

    # Nonnegativity - lower bounds
    model.addConstrs((d[i, j] >= 0 for (i,j) in model_edges_without_I), name='d_nonneg')
    model.addConstrs((m[i] >= 0 for i in model_nodes_without_I), name='mu_nonneg')
    model.addConstrs((f[i, j] >= 0 for (i,j) in model_edges), name='f_nonneg')
    # model.addConstrs((d_aux[i, j] >= 0 for (i,j) in model_edges), name='d_aux_nonneg')

    # upper bounds
    model.addConstrs((d[i, j] <= 1 for (i,j) in model_edges_without_I), name='d_upper_b')
    model.addConstrs((m[i] <= 1 for i in model_nodes_without_I), name='mu_upper_b')
    # model.addConstrs((d_aux[i, j] <= 1 for (i,j) in model_edges), name='d_aux_upper_b')
    # capacity (upper bound for f)
    model.addConstrs((f[i, j] <= 1 for (i,j) in model_edges), name='capacity')

    # preserve flow
    model.addConstr((1 <= sum(f[i,j] for (i, j) in model_edges if i in src)), name='conserve_F')

    # conservation
    model.addConstrs((sum(f[i,j] for (i,j) in model_edges if j == l) == sum(f[i,j] for (i,j) in model_edges if i == l) for l in model_nodes if l not in src and l not in sink), name='conservation')

    # no in source or out of sink
    model.addConstrs((f[i,j] == 0 for (i,j) in model_edges if j in src or i in sink), name="no_out_sink_in_src")

    # cut constraint
    model.addConstrs((f[i,j] + d[i,j] <= 1 for (i,j) in model_edges_without_I), name='cut_cons')

    # # map d to d_aux
    # model.addConstrs((d[i,j] == d_aux[i,j] for (i,j) in model_edges_without_I), name='match_d_to_all_edges')

    # source sink partitions
    for i in model_nodes_without_I:
        for j in model_nodes_without_I:
            if i in src and j in sink:
                model.addConstr(m[i] - m[j] >= 1)

    # max flow cut constraint
    model.addConstrs((d[i,j] - m[i] + m[j] >= 0 for (i,j) in model_edges_without_I))

    # --------- add feasibility constraints to preserve flow F_s >=1 on S for every q

    node_list = []
    for node in G.nodes:
        node_list.append(GD.node_dict[node])

    qs = list(set([node[-1] for node in node_list]))

    # get the source/sink pairs (sink always T) for the history variables q
    s_srcs = {}
    for q in qs:
        transition_nodes = []
        for edge in G.edges:
            out_edge = GD.node_dict[edge[0]]
            in_edge = GD.node_dict[edge[1]]
            if in_edge[-1] == q and out_edge[-1] != q:
                node = edge[1]
                s_node = map_G_to_S[node]
                transition_nodes.append(s_node)
        clean_transition_nodes = list(set(transition_nodes))
        s_srcs.update({q: clean_transition_nodes})
    s_srcs.update({'q0': SD.init})

    s_data = []
    for q in qs:
        for k,s in enumerate(s_srcs[q]):
            name = 'fS_'+ str(q) +'_'+ str(k)
            source = s
            s_data.append((name, q, source))

    f_s = [None for entry in s_data]
    for k,entry in enumerate(s_data):
        name = entry[0]
        curr_q = entry[1]
        s_src = [entry[2]]
        if entry[2] not in s_sink:

            f_s[k] = model.addVars(model_s_edges, name=name)

            # nonnegativity for f_s (lower bound)
            model.addConstrs((f_s[k][i, j] >= 0 for (i,j) in model_s_edges), name= name + '_nonneg')

            # capacity on S (upper bound on f_s)
            model.addConstrs((f_s[k][i, j] <= 1 for (i,j) in model_s_edges), name=name+ '_capacity')

            # Preserve flow of 1 in S
            model.addConstr((1 <= sum(f_s[k][i,j] for (i, j) in model_s_edges if j in s_sink)), name=name + '_conserve_flow_1')

            # conservation on S
            model.addConstrs((sum(f_s[k][i,j] for (i,j) in model_s_edges if j == l) == sum(f_s[k][i,j] for (i,j) in model_s_edges if i == l) for l in model_s_nodes if l not in s_src and l not in s_sink), name=name+'_conservation')

            # no flow into sources and out of sinks on S
            model.addConstrs((f_s[k][i,j] == 0 for (i,j) in model_s_edges if j in s_src or i in s_sink), name=name+ '_sink_src')

            # Match the edge cuts from G to S
            for (i,j) in model_edges_without_I:
                if GD.node_dict[i][-1] == curr_q:
                    imap = map_G_to_S[i]
                    jmap = map_G_to_S[j]
                    model.addConstr(f_s[k][imap, jmap] + d[i, j] <= 1)

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
    # elif model.status == 11:
    #     if model.SolCount <= 1:
    #
    #         model.optimize(callback=cb_max)
    #         if model.SolCount <= 1:
    #             exit_status = 'not solved'
    #             return exit_status, [], [], None

    elif model.status == 2 or model.status == 11:
        if model.status == 11 and model.SolCount < 1:
            # model.optimize(callback=cb)
            # if model.SolCount <= 1:
            exit_status = 'not solved'
            return exit_status, [], [], None
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

    else:
        st()

    return exit_status, f_vals, d_vals, flow