'''
Gurobipy implementation of the MILP for mixed obstacles (static + reactive).
'''

import gurobipy as gp
from gurobipy import GRB
import time
import numpy as np
from ipdb import set_trace as st
import networkx as nx
from optimization.feasibility_constraints import find_map_G_S, find_map_G_S_w_fuel
from gurobipy import *
from copy import deepcopy
import os 
import json

# New Callback Function:
# Callback function
def new_cb(model, where):
    if where == GRB.Callback.MIPNODE:
        # Get model objective
        obj = model.cbGet(GRB.Callback.MIPNODE_OBJBST) # Current best objective
        opt_time = model.cbGet(GRB.Callback.RUNTIME) # Optimizer runtime
        obj_bound = model.cbGet(GRB.Callback.MIPNODE_OBJBND) # Objective bound
        node_count = model.cbGet(GRB.Callback.MIPNODE_NODCNT) # No. of unexplored nodes 
        sol_count = model.cbGet(GRB.Callback.MIPNODE_SOLCNT) # No. of feasible solns found.

        # Save model and opt data:
        model._data["opt_time"].append(opt_time)
        model._data["best_obj"].append(obj)
        model._data["bound"].append(obj_bound)
        model._data["node_count"].append(node_count)
        model._data["sol_count"].append(sol_count)

        # 5 iterations.
        # cur_obj to float(np.inf)
        # Has objective changed?
        if abs(obj - model._cur_obj) > 1e-8:
            # If so, update incumbent and time
            model._cur_obj = obj
            model._time = time.time()
            
        # Terminate if objective has not improved in 30s
        # Current objective is less than infinity.
        if obj < float(np.inf):
            # if time.time() - model._time > 30:# and model.SolCount >= 1:
            if len(model._data["best_obj"]) > 5:
                last_five = model._data["best_obj"][-5:]
                if last_five.count(last_five[0]) == len(last_five): # If the objective has not changed in 5 iterations, terminate
                    model.terminate()
        else:
            # Total termination time if the optimizer has not found anything in 5 min:
            if time.time() - model._time > 3000: 
                model.terminate()

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
def solve_max_gurobi(GD, SD, static_area = [], excluded_sols = []):
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
    map_G_to_S_w_fuel = find_map_G_S_w_fuel(GD,SD)
    map_G_to_S = find_map_G_S(GD,SD)

    s_sink = SD.acc_sys

    model_s_edges = list(S.edges)
    model_s_nodes = list(S.nodes)

    # st()
    model = Model()

    # --------- set parameters
    # Last updated objective and time (for callback function)
    model.Params.NumericFocus=2
    model._cur_obj = float('inf')
    model._time = time.time()
    model.Params.Seed = np.random.randint(0,100)
    model._data = dict() # To store objective data.
    for key in ["opt_time", "best_obj", "bound", "node_count", "sol_count"]:
        model._data[key] = []
    # add variables
    # outer player
    f = model.addVars(model_edges, name="flow")
    # inner player
    d = model.addVars(model_edges, vtype=GRB.BINARY, name="d") # Binary variable
    m = model.addVars(model_nodes_without_I, name="m")

    # to count incoming cuts
    # inc = model.addVars(model_nodes, name="inc")

    # Define Objective
    term = sum(f[i,j] for (i, j) in model_edges if i in src)
    ncuts = sum(d[i,j] for (i, j) in model_edges)
    # ncuts_weighted = sum(inc[i] for i in model_nodes)
    regularizer = 1/len(model_edges)

    model.setObjective(term - regularizer*ncuts, GRB.MAXIMIZE)

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
    # model.addConstrs((inc[k] == max_(d[i,j] for (i,j) in model_edges if j == k) for k in model_nodes), name='inc_match')


    # --------- add static constraints to every state outside of reactive_area
    # st()
    for count, (i,j) in enumerate(model_edges):
        out_state = GD.node_dict[i][0]
        in_state = GD.node_dict[j][0]

        if GD.node_dict[i][0][0] == (2, 5):
            # st()
            pass

        if out_state in static_area and in_state in static_area:
            for (imap,jmap) in model_edges[count+1:]:
                if out_state[0] == GD.node_dict[imap][0][0] and in_state[0] == GD.node_dict[jmap][0][0]:
                    model.addConstr(d[i, j] == d[imap, jmap])

    # --------- add feasibility constraints to preserve flow F_s >=1 on S for every q

    node_list = []
    for node in G.nodes:
        node_list.append(GD.node_dict[node])

    qs = list(set([node[-1] for node in node_list]))

    # get the source/sink pairs (sink always T) for the history variables q
    # st()
    s_srcs = {}
    for q in qs:
        transition_nodes = []
        for edge in G.edges:
            out_edge = GD.node_dict[edge[0]]
            in_edge = GD.node_dict[edge[1]]
            if in_edge[-1] == q and out_edge[-1] != q:
                node = edge[1]
                s_node = map_G_to_S[node]
                for target in s_sink:
                    if nx.has_path(S,s_node,target):
                        transition_nodes.append(s_node)
        clean_transition_nodes = list(set(transition_nodes))
        s_srcs.update({q: clean_transition_nodes})
    s_srcs.update({'q0': SD.init})
    # st()

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
            # st()
            for (i,j) in model_edges:
                out_state = GD.node_dict[i][0]
                in_state = GD.node_dict[j][0]

                imaplist = map_G_to_S_w_fuel[i]
                jmaplist = map_G_to_S_w_fuel[j]

                if out_state and in_state in static_area:
                    for imap in imaplist:
                        for jmap in jmaplist:
                            if (imap,jmap) in model_s_edges:
                                model.addConstr(f_s[k][imap, jmap] + d[i, j] <= 1)
                elif GD.node_dict[i][-1] == curr_q:
                    for imap in imaplist:
                        for jmap in jmaplist:
                            if (imap,jmap) in model_s_edges:
                                model.addConstr(f_s[k][imap, jmap] + d[i, j] <= 1)
    # st()

    # --- Exclude specific solutions that cannot be realized
    # st()
    for excluded_sol in excluded_sols:
        model.addConstr(sum(d[i, j] for (i,j) in excluded_sol) <= len(excluded_sol)-1)
    model._data["n_cex"] = len(excluded_sols)

    # model.Params.InfUnbdInfo = 1

    # optimize
    model.optimize(callback=new_cb)

    model._data["runtime"] = model.Runtime
    model._data["n_bin_vars"] = model.NumBinVars
    model._data["n_cont_vars"] = model.NumVars - model.NumBinVars
    model._data["n_constrs"] = model.NumConstrs


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
        
    if not os.path.exists("log"):
        os.makedirs("log")
    with open('log/opt_data.json', 'w') as fp:
        json.dump(model._data, fp)

    return exit_status, f_vals, d_vals, flow
