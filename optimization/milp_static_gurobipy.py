'''
Gurobipy implementation of the MILP for static obstacles.
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
import os
import json

# Callback with storage:
CB_OBJ_CONST = 5
# Callback function
def rand_cb(model, where):
    if where == GRB.Callback.MIPNODE:
        # Get model objective
        obj = model.cbGet(GRB.Callback.MIPNODE_OBJBST) # Current best objective
        # opt_time = model.cbGet(GRB.Callback.RUNTIME) # Optimizer time
        # obj_bound = model.cbGet(GRB.Callback.MIPNODE_OBJBND) # Objective bound
        # node_count = model.cbGet(GRB.Callback.MIPNODE_NODCNT) # No. of unexplored nodes
        sol_count = model.cbGet(GRB.Callback.MIPNODE_SOLCNT) # No. of feasible solns found.

        # Save model and opt data:
        # model._extra_data["opt_time"].append(opt_time)
        # model._extra_data["best_obj"].append(obj)
        # model._extra_data["bound"].append(obj_bound)
        # model._extra_data["node_count"].append(node_count)
        # model._extra_data["sol_count"].append(sol_count)

        # 5 iterations.
        # cur_obj to float(np.inf)
        # Has objective changed?
        if abs(obj - model._cur_obj) > 1e-8:
            # If so, update incumbent and time
            model._cur_obj = obj
            # model._time = time.time()

        # Terminate if objective has not improved in 30s
        # Current objective is less than infinity.

        # if obj < float(np.inf):
        if sol_count > 1:
            if time.time() - model._time > 60:
                model._data["term_condition"] = "Obj not changing"
                model.terminate()
            # if time.time() - model._time > 30:# and model.SolCount >= 1:
            # if len(model._extra_data["best_obj"]) > CB_OBJ_CONST:
            #     last_few_objs = model._extra_data["best_obj"][-CB_OBJ_CONST:]
            #     if last_few.count(last_few_objs[0]) == len(last_few_objs): # If the objective has not changed in 5 iterations, terminate
            #         model._data["term_condition"] = "Obj not changing"
            #         model.terminate()

        else:
            # Total termination time if the optimizer has not found anything in 5 min:
            if time.time() - model._time > 600:
                model._data["term_condition"] = "Timeout"
                model.terminate()

# Callback function
def exp_cb(model, where):
    if where == GRB.Callback.MIPNODE:
        # Get model objective
        obj = model.cbGet(GRB.Callback.MIPNODE_OBJBST)
        model._extra_data["best_obj"].append(obj)
        # Has objective changed?
        if abs(obj - model._cur_obj) > 1e-8:
            # If so, update incumbent and time
            model._cur_obj = obj
            model._time = time.time()

    # Terminate if objective has not improved in 30s
    if time.time() - model._time > 600:# and model.SolCount >= 1:
        model.terminate()

# Gurobi implementation
def solve_max_gurobi(GD, SD, callback="exp_cb", logger=None, logger_runtime_dict=None):
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
    d = model.addVars(model_edges, vtype=GRB.BINARY, name="d")
    # inner player
    m = model.addVars(model_nodes_without_I, name="m")

    # Define Objective
    term = sum(f[i,j] for (i, j) in model_edges if i in src)
    ncuts = sum(d[i,j] for (i, j) in model_edges)
    reg = 1/len(model_edges)
    model.setObjective(term - reg*ncuts, GRB.MAXIMIZE)

    # Nonnegativity - lower bounds
    model.addConstrs((d[i, j] >= 0 for (i,j) in model_edges), name='d_nonneg')
    model.addConstrs((m[i] >= 0 for i in model_nodes_without_I), name='mu_nonneg')
    model.addConstrs((f[i, j] >= 0 for (i,j) in model_edges), name='f_nonneg')

    # upper bounds
    model.addConstrs((d[i, j] <= 1 for (i,j) in model_edges), name='d_upper_b')
    model.addConstrs((m[i] <= 1 for i in model_nodes_without_I), name='mu_upper_b')
    # capacity (upper bound for f)
    model.addConstrs((f[i, j] <= 1 for (i,j) in model_edges), name='capacity')

    # preserve flow
    model.addConstr((1 <= sum(f[i,j] for (i, j) in model_edges if i in src)), name='conserve_F')

    # conservation
    model.addConstrs((sum(f[i,j] for (i,j) in model_edges if j == l) == sum(f[i,j] for (i,j) in model_edges if i == l) for l in model_nodes if l not in src and l not in sink), name='conservation')

    # no in source or out of sink
    model.addConstrs((f[i,j] == 0 for (i,j) in model_edges if j in src or i in sink), name="no_out_sink_in_src")

    # cut constraint
    model.addConstrs((f[i,j] + d[i,j] <= 1 for (i,j) in model_edges), name='cut_cons')

    # source sink partitions
    for i in model_nodes_without_I:
        for j in model_nodes_without_I:
            if i in src and j in sink:
                model.addConstr(m[i] - m[j] >= 1)

    # max flow cut constraint
    model.addConstrs((d[i,j] - m[i] + m[j] >= 0 for (i,j) in model_edges_without_I))


    # --------- add feasibility constraints to preserve flow f_s on S
    # f_s = model.addVars(model_s_edges, name="flow_on_S")

    # # nonnegativitiy for f_s (lower bound)
    # model.addConstrs((f_s[i, j] >= 0 for (i,j) in model_s_edges), name='f_s_nonneg')

    # # capacity on S (upper bound on f_s)
    # model.addConstrs((f_s[i, j] <= 1 for (i,j) in model_s_edges), name='capacity_f_S')

    # # Match the edge cuts from G to S
    # for (i,j) in model_edges:
    #     imap = map_G_to_S[i]
    #     jmap = map_G_to_S[j]
    #     if (imap,jmap) in model_s_edges:
    #         model.addConstr(f_s[imap, jmap] + d[i, j] <= 1)

    # # Preserve flow of 1 in S
    # model.addConstr((1 <= sum(f_s[i,j] for (i, j) in model_s_edges if i == s_src)), name='conserve_F_on_S')

    # # conservation on S
    # model.addConstrs((sum(f_s[i,j] for (i,j) in model_s_edges if j == l) == sum(f_s[i,j] for (i,j) in model_s_edges if i == l) for l in model_s_nodes if l != s_src and l not in s_sink), name='conservation_f_S')

    # # no flow into sources and out of sinks on S
    # model.addConstrs((f_s[i,j] == 0 for (i,j) in model_s_edges if j == s_src or i in s_sink), name="no_out_sink_in_src_on_S")


    # --------- map static obstacles to other edges in G
    for count, (i,j) in enumerate(model_edges):
        out_state = GD.node_dict[i][0]
        in_state = GD.node_dict[j][0]
        for (imap,jmap) in model_edges[count+1:]:
            if out_state == GD.node_dict[imap][0] and in_state == GD.node_dict[jmap][0]:
                model.addConstr(d[i, j] == d[imap, jmap])


    # ---------  add bidirectional cuts on G
    for count, (i,j) in enumerate(model_edges):
        out_state = GD.node_dict[i][0]
        in_state = GD.node_dict[j][0]
        for (imap,jmap) in model_edges[count+1:]:
            if in_state == GD.node_dict[imap][0] and out_state == GD.node_dict[jmap][0]:
                model.addConstr(d[i, j] == d[imap, jmap])

    # --------- set parameters
    # Last updated objective and time (for callback function)
    model._cur_obj = float('inf')
    model._time = time.time()
    model.Params.Seed = np.random.randint(0,100)
    model._data = dict()
    model._extra_data = dict() # To store objective data.
    for key in ["opt_time", "best_obj", "bound", "node_count", "sol_count"]:
        model._extra_data[key] = []
    model._data["term_condition"] = None

    # model.Params.InfUnbdInfo = 1
    # optimize
    if callback=="exp_cb":
        model.optimize(callback=exp_cb)
    if callback=="rand_cb":
        model.optimize(callback=rand_cb)
    else:
        model.optimize()

    model._data["runtime"] = model.Runtime
    model._data["flow"] = None
    model._data["ncuts"] = None

    # Storing problem variables:
    model._data["n_bin_vars"] = model.NumBinVars
    model._data["n_cont_vars"] = model.NumVars - model.NumBinVars
    model._data["n_constrs"] = model.NumConstrs

    # model.Params.InfUnbdInfo = 1
    f_vals = []
    d_vals = []
    flow = None
    exit_status = None

    if model.status == 4:
        model.Params.DualReductions = 0
        # model.optimize(callback="exp_cb")

        exit_status = 'inf'
        model._data["status"] = "inf/unbounded"
    # elif model.status == 11:
    #     if model.SolCount <= 1:
    #
    #         model.optimize(callback=cb_max)
    #         if model.SolCount <= 1:
    #             exit_status = 'not solved'
    #             return exit_status, [], [], None
    elif model.status == 11 and model.SolCount < 1:
        exit_status = 'not solved'
        model._data["status"] = "not_solved"
        model._data["exit_status"] = exit_status

    elif model.status == 2 or (model.status == 11 and model.SolCount >= 1):
        if model.status == 2:
            model._data["status"] = "optimal"
            model._data["term_condition"] = "optimal found"
        else:
            # feasible. maybe be optimal.
            model._data["status"] = "feasible"

        # --------- parse output
        d_vals = dict()
        f_vals = dict()

        try:
            for (i,j) in model_edges:
                f_vals.update({(i,j): f[i,j].X})
            for (i,j) in model_edges:
                d_vals.update({(i,j): d[i,j].X})
        except:
            st()

        flow = sum(f[i,j].X for (i,j) in model_edges if i in src)
        model._data["flow"] = flow
        ncuts = 0

        for key in d_vals.keys():
            if d_vals[key] > 0.9:
                ncuts+=1
                print('{0} to {1} at {2}'.format(GD.node_dict[key[0]], GD.node_dict[key[1]],d_vals[key]))

        model._data["ncuts"] = ncuts
        exit_status = 'opt'
        model._data["exit_status"] = exit_status

    elif model.status == 3:
        exit_status = 'inf'
        model._data["status"] = "inf"

    else:
        st()

    if not os.path.exists("log"):
        os.makedirs("log")
    if logger is None:
        with open('log/opt_data.json', 'w') as fp:
            json.dump(model._data, fp)
        with open('log/extra_opt_data.json', 'w') as fp:
            json.dump(model._extra_data, fp)
    else:
        logger.save_optimization_data(model._data)
        logger.save_optimization_data(model._extra_data, fn="extra_opt_data")
        logger_runtime_dict["opt_runtimes"].append(model._data["runtime"])

    return exit_status, f_vals, d_vals, flow
