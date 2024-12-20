'''
Gurobipy implementation of the MILP for mixed obstacles (static + reactive) with augmented objective.
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

# New Callback function
def rand_cb(model, where):
    if where == GRB.Callback.MIPNODE:
        # Get model objective
        obj = model.cbGet(GRB.Callback.MIPNODE_OBJBST) # Current best objective
        opt_time = model.cbGet(GRB.Callback.RUNTIME) # Optimizer runtime
        obj_bound = model.cbGet(GRB.Callback.MIPNODE_OBJBND) # Objective bound
        node_count = model.cbGet(GRB.Callback.MIPNODE_NODCNT) # No. of unexplored nodes
        sol_count = model.cbGet(GRB.Callback.MIPNODE_SOLCNT) # No. of feasible solns found.

        # Save model and opt data:
        model._extra_data["opt_time"].append(opt_time)
        model._extra_data["best_obj"].append(obj)
        model._extra_data["bound"].append(obj_bound)
        model._extra_data["node_count"].append(node_count)
        model._extra_data["sol_count"].append(sol_count)

        # 5 iterations.
        # cur_obj to float(np.inf)
        # Has objective changed?
        if abs(obj - model._cur_obj) > 1e-8:
            # If so, update incumbent and time
            model._cur_obj = obj
            model._time = time.time()

        # Terminate if objective has not improved in 30s
        # Current objective is less than infinity.
        if sol_count >= 1:
            if time.time() - model._time > 120:
                model._data["term_condition"] = "Obj not changing"
                model.terminate()
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

        # Has objective changed?
        if abs(obj - model._cur_obj) > 1e-8:
            # If so, update incumbent and time
            model._cur_obj = obj
            model._time = time.time()

    # Terminate if objective has not improved in 30s
    if time.time() - model._time > 30:# and model.SolCount >= 1:
        model.terminate()

# Gurobi implementation
def solve_max_gurobi(GD, SD, static_area = [], excluded_sols = [], callback="exp_cb",logger=None, logger_runtime_dict=None, alpha = 0.8):
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
    G_minus_I.remove_nodes_from(cleaned_intermed)

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

    model_s_edges = list(S.edges)
    model_s_nodes = list(S.nodes)

    model = Model()
    # --------- set parameters
    # Last updated objective and time (for callback function)
    model._cur_obj = float('inf')
    model._time = time.time()
    model.Params.Seed = np.random.randint(0,100)
    model._data = dict() # To store objective data.
    model._extra_data = dict()
    for key in ["opt_time", "best_obj", "bound", "node_count", "sol_count"]:
        model._extra_data[key] = []
    model._data["flow"] = None
    model._data["ncuts"] = None

    # add variables
    # outer player
    f = model.addVars(model_edges, name="flow")
    # inner player
    d = model.addVars(model_edges, vtype=GRB.BINARY, name="d") # Binary variable
    m = model.addVars(model_nodes_without_I, name="m")

    # to count incoming cuts
    inc = model.addVars(model_nodes, name="inc")

    # Define Objective
    term = sum(f[i,j] for (i, j) in model_edges if i in src)
    ncuts = sum(d[i,j] for (i, j) in model_edges)
    ncuts_weighted = sum(inc[i] for i in model_nodes)
    n_nodes = len(model_nodes)
    n_edges = len(model_edges)
    
    model.setObjective(term - 1/(1+n_edges)*ncuts - 1/((1+n_edges)*n_nodes)*ncuts_weighted, GRB.MAXIMIZE)

    # model.setObjective(term - alpha*regularizer_nodes*ncuts_weighted - (1-alpha)*regularizer_edges*ncuts, GRB.MAXIMIZE)

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

    # count incoming cuts
    model.addConstrs((inc[k] == max_(d[i,j] for (i,j) in model_edges if j == k) for k in model_nodes), name='inc_match')


    # --------- add static constraints to every state outside of reactive_area
    for count, (i,j) in enumerate(model_edges):
        out_state = GD.node_dict[i][0]
        in_state = GD.node_dict[j][0]

        if in_state in static_area:
            for (imap,jmap) in model_edges[count+1:]:
                if out_state == GD.node_dict[imap][0] and in_state == GD.node_dict[jmap][0]:
                    # st()
                    if out_state == (3,0) and in_state == (2,0):
                        print(GD.node_dict[i], GD.node_dict[j])
                        print(GD.node_dict[imap], GD.node_dict[jmap])
                    model.addConstr(d[i, j] == d[imap, jmap])

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
                # s_node = map_G_to_S[node]
                # transition_nodes.append(s_node)
                s_nodes = map_G_to_S[node]
                for target in s_sink:
                    for s_node in s_nodes:
                        if nx.has_path(S,s_node,target):
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
            for (i,j) in model_edges:
                out_state = GD.node_dict[i][0]
                in_state = GD.node_dict[j][0]

                imaps = map_G_to_S[i]
                jmaps = map_G_to_S[j]

                for imap in imaps:
                    for jmap in jmaps:
                        if (imap,jmap) in SD.edges:
                            if out_state and in_state in static_area:
                                model.addConstr(f_s[k][imap, jmap] + d[i, j] <= 1)
                            elif GD.node_dict[i][-1] == curr_q:
                                model.addConstr(f_s[k][imap, jmap] + d[i, j] <= 1)

    # --- Exclude specific solutions that cannot be realized
    # st()
    for excluded_sol in excluded_sols:
        model.addConstr(sum(d[i, j] for (i,j) in model_edges) - sum(d[i, j] for (i,j) in excluded_sol) >= 1)
    model._data["n_cex"] = len(excluded_sols)

    # model.Params.InfUnbdInfo = 1

    # optimize
    if callback=="exp_cb":
        model.optimize(callback=exp_cb)
    elif callback=="rand_cb":
        model.optimize(callback=rand_cb)
    else:
        model.optimize()

    model._data["runtime"] = model.Runtime

    model._data["n_bin_vars"] = model.NumBinVars
    model._data["n_cont_vars"] = model.NumVars - model.NumBinVars
    model._data["n_constrs"] = model.NumConstrs

    f_vals = []
    d_vals = []
    flow = None

    if model.status == 4:
        model.Params.DualReductions = 0
        model.optimize(callback="exp_cb")

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
        else:
            # feasible. maybe be optimal.
            model._data["status"] = "feasible"

        # --------- parse output
        d_vals = dict()
        f_vals = dict()

        for (i,j) in model_edges:
            f_vals.update({(i,j): f[i,j].X})
        for (i,j) in model_edges:
            d_vals.update({(i,j): d[i,j].X})

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
