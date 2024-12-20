# This file setups the problem data for gradient_descent.py
# Finding constraints as: Ax - b >= 0
import sys
sys.path.append('..')
sys.path.append('../../Flow-Constraints/')

import numpy as np
from ipdb import set_trace as st
from collections import OrderedDict as od
import _pickle as pickle
import os
import networkx as nx
import matplotlib.pyplot as plt
from scipy import sparse as sp
import pdb
from construct_automata.main import quad_test_sync
from find_cuts import setup_nodes_and_edges, get_graph

def initialize():
    virtual, system, b_pi, virtual_sys = quad_test_sync()
    GD, S = setup_nodes_and_edges(virtual, virtual_sys, b_pi)
    G = get_graph(nodes, edges)
    # remove self loops
    edges = list(G.edges())
    for i,j in edges:
        if i == j:
            G.remove_edge(i,j)
    nodes = list(G.nodes())
    nodes_keys = {k: v for k,v in enumerate(nodes)}
    edges = list(G.edges())
    edges_keys = {k: e for k,e in enumerate(edges)}
    vars_x = ['ft', 'd', 'F']
    vars_y = ['fs']
    edges_dict = {k: 0 for k in edges} # Edges have flow.
    x = {k: edges_dict for k in vars_x}
    y = {k: edges_dict for k in vars_y}
    return x, y, G, nodes_keys, edges_keys

# Prefix z: zeros
def objective(edges_keys):
    ne = len(list(edges_keys.keys())) # number of edges
    zft = np.zeros((ne,1))
    ofs = np.zeros((ne,1))
    zd = np.zeros((ne,1))
    ot = 1.0/ne*np.ones((1,1))

    c1 = np.vstack((zft, zd, ot)) # zf: zero vector for f, and ot: one vector for t
    # !!!!
    c2 = ofs.copy()
    
    # Objective function: c1.T x + c2.T y
    return c1, c2

def populate_constraint_names(name_list, edges_keys=None, nodes_keys=None):
    constraint_names = []
    if edges_keys:
        for k, edge in edges_keys.items():
            for name in name_list:
                if isinstance(edge[0], tuple):
                    edge_str = str(edge[0][0])+","+str(edge[0][1])+","+str(edge[1][0])+","+str(edge[1][1])
                else:
                    edge_str = str(edge[0])+","+str(edge[1])
                constraint_names.append(name+"["+edge_str+"]")
    elif nodes_keys:
        for k, node in nodes_keys.items():
            for name in name_list:
                if isinstance(node, tuple):
                    node_str = str(node[0])+","+str(node[1])
                else:
                    node_str = str(node)
                constraint_names.append(name+"["+node_str+"]")
    return constraint_names

# Nonnegativity constraint:
def nonneg_constraint(edges_keys, projection=False):
    feas_names = []
    ne = len(list(edges_keys.keys())) # number of edges
    Aft = np.eye(ne)
    Afs = np.eye(ne)
    Ad = np.eye(ne)
    zot = np.zeros((ne,1))
    blk_zeros = np.zeros((ne,ne))

    # x constraints
    if projection:
        b_feas = np.zeros((2*ne,1))
        feas_constraints_names = ["nonnegt", "nonnegd"]
        A_feas_ft= np.hstack((Aft, blk_zeros, zot))
        A_feas_de= np.hstack((blk_zeros, Ad, zot))
        A_feas = np.vstack((A_feas_ft, A_feas_de))
    else:
        b_feas = np.zeros((3*ne,1))
        feas_constraints_names = ["capt", "capd", "caps"]
        A_feas_ft= np.hstack((Aft, blk_zeros, zot, blk_zeros))
        A_feas_fs= np.hstack((blk_zeros, blk_zeros, zot, Afs))
        A_feas_d= np.hstack((blk_zeros, Ad, zot, blk_zeros))
        A_feas = np.vstack((A_feas_ft, A_feas_d, A_feas_fs))
    feas_names = populate_constraint_names(feas_constraints_names, edges_keys=edges_keys)
    assert A_feas.shape[0] == b_feas.shape[0]
    return A_feas, b_feas, feas_names

# Capacity constraint
def capacity_constraint(edges_keys, projection=False):
    feas_names = []
    ne = len(list(edges_keys.keys())) # number of edges
    Aft = -1*np.eye(ne)
    Afs = -1*np.eye(ne)
    Ad = -1*np.eye(ne)
    Aot = np.ones((ne,1))
    blk_zeros = np.zeros((ne,ne))

    # x constraints
    if projection:
        b_feas = np.zeros((2*ne,1))
        feas_constraints_names = ["capt", "capd"]
        A_feas_ft= np.hstack((Aft, blk_zeros, Aot))
        A_feas_de= np.hstack((blk_zeros, Ad, Aot))
        A_feas = np.vstack((A_feas_ft, A_feas_de))
    else:
        b_feas = np.zeros((3*ne,1))
        feas_constraints_names = ["capt", "capd", "caps"]
        A_feas_ft= np.hstack((Aft, blk_zeros, Aot, blk_zeros))
        A_feas_fs= np.hstack((blk_zeros, blk_zeros, Aot, Afs))
        A_feas_d= np.hstack((blk_zeros, Ad, Aot, blk_zeros))
        A_feas = np.vstack((A_feas_ft, A_feas_d, A_feas_fs))
    feas_names = populate_constraint_names(feas_constraints_names, edges_keys=edges_keys)
    assert A_feas.shape[0] == b_feas.shape[0]
    return A_feas, b_feas, feas_names

# Conservation constraint
def conservation_helper_function(edges_keys, nodes_keys, start, target, con_names):
    ne = len(list(edges_keys.keys())) # number of edges
    nv = len(list(nodes_keys.keys())) # number of edges

    exclude_nodes = []
    if isinstance(start, list):
        exclude_nodes.extend(start)
    else:
        exclude_nodes.append(start)
    if isinstance(target, list):
        exclude_nodes.extend(target)
    else:
        exclude_nodes.append(target)
    module_mtrx = np.zeros((nv-len(exclude_nodes),ne)) # One matrix for holding all conservation terms except for the source and target.
    Afeas = module_mtrx.copy()
    nodes_keys_subset = dict()
    j=0
    for k,node in nodes_keys.items():
        if node not in exclude_nodes:
            nodes_keys_subset.update({k:node})
            out_node_edge_ind = [k for k, v in edges_keys.items() if v[0]==node]
            in_node_edge_ind = [k for k, v in edges_keys.items() if v[1]==node]
            for out_ind in out_node_edge_ind:
                Afeas[j][out_ind] = -1
            for in_ind in in_node_edge_ind:
                Afeas[j][in_ind] = 1
            j += 1
    con = populate_constraint_names(con_names, edges_keys=None, nodes_keys=nodes_keys_subset)
    return Afeas, con

def proj_conservation_constraint(nodes_keys, edges_keys, src, int, sink):
    cons_names =[]
    ne = len(list(edges_keys.keys())) # number of edges
    nv = len(list(nodes_keys.keys())) # number of edges

    Afeas_ft, con_ft = conservation_helper_function(edges_keys, nodes_keys, src, int,["const"])

    nv1 =  len(con_ft)
    module_mtrx1 = np.zeros((nv1,ne)) # One matrix for holding all conservation
    module_vec1 = np.zeros((nv1,1))

    # Constructing block matrices:
    Acons_f1 = np.hstack((Afeas_ft, module_mtrx1, module_vec1))
    # Final assembly:
    cons_names.extend(con_ft)

    assert Acons_f1.shape[0] == module_vec1.shape[0]
    return Acons_f1, module_vec1, cons_names

def conservation_constraint(nodes_keys, edges_keys, src, int, sink):
    #  Equality cosntraints Acons, bcons
    cons_names =[]
    ne = len(list(edges_keys.keys())) # number of edges
    nv = len(list(nodes_keys.keys())) # number of edges

    Afeas_ft, con_ft = conservation_helper_function(edges_keys, nodes_keys, src, int,["cons_test"])
    Afeas_fs,con_fs= conservation_helper_function(edges_keys, nodes_keys, src, sink, ["cons_sys"])

    nv_t, nv_s = len(con_ft), len(con_fs)
    module_mtrx1 = np.zeros((nv_t,ne)) # One matrix for holding all conservation
    module_vec1 = np.zeros((nv_t,1))

    module_mtrx3 = np.zeros((nv_s,ne)) # One matrix for holding all conservation
    module_vec3 = np.zeros((nv_s,1))

    # Constructing block matrices:
    Acons_ft = np.hstack((Afeas_ft, module_mtrx1, module_vec1, module_mtrx1))
    Acons_fs = np.hstack((module_mtrx3, module_mtrx3, module_vec3, Afeas_fs))

    # Final assembly:
    cons_names.extend(con_ft)
    cons_names.extend(con_fs)

    Acons = np.vstack((Acons_ft, Acons_fs))
    bcons = np.vstack((module_vec1, module_vec3))
    try:
        assert len(cons_names) == Acons.shape[0]
        assert Acons.shape[0] == bcons.shape[0]
    except:
        pdb.set_trace()
    return Acons, bcons, cons_names

# Cut constraint:
def cut_constraint(edges_keys, projection=False):
    cut_names = []
    ne = len(list(edges_keys.keys())) # number of edges
    Aft = -1*np.eye(ne)
    Afs = -1*np.eye(ne)
    Ad = -1*np.eye(ne)
    Aot = np.ones((ne,1))
    blk_zeros = np.zeros((ne,ne))

    if projection:
        cut_constraints_names = ["cut_cons_t"]
        A_feas= np.hstack((Aft, Ad, Aot))
        b_feas = np.zeros((ne,1))
    else:
        cut_constraints_names = ["cut_cons_t", "cut_cons_s"]
        A_feas_ft= np.hstack((Aft, Ad, Aot, blk_zeros))
        A_feas_fs= np.hstack((blk_zeros, Ad, Aot, Afs))
        A_feas = np.vstack((A_feas_ft, A_feas_fs))
        b_feas = np.zeros((2*ne,1))
    cut_names = populate_constraint_names(cut_constraints_names, edges_keys=edges_keys)

    assert A_feas.shape[0] == b_feas.shape[0]
    return A_feas, b_feas, cut_names

# No in source
def no_in_source(edges_keys, src, int, sink, projection=False):
    flow_names = []

    ne = len(list(edges_keys.keys())) # number of edges

    in_s1_edge_ind = [k for k, v in edges_keys.items() if v[1] in src]
    in_s3_edge_ind = [k for k, v in edges_keys.items() if v[1] in src]

    aft = np.zeros((len(in_s1_edge_ind), ne))
    afs = np.zeros((len(in_s3_edge_ind), ne))

    s1_edges = dict()
    s2_edges = dict()
    s3_edges = dict()
    for i, k in enumerate(in_s1_edge_ind):
        s1_edges[k] = edges_keys[k]
        aft[i, k] = 1

    for i, k in enumerate(in_s3_edge_ind):
        s3_edges[k] = edges_keys[k]
        afs[i, k] = 1

    flow_names1 = populate_constraint_names(["no_in_source_test"], edges_keys=s1_edges)
    flow_names.extend(flow_names1)
    if projection:
        Afeas = np.hstack((aft, 0*aft, np.zeros((aft.shape[0],1))))
    else:
        a1 = np.hstack((aft, 0*aft, np.zeros((aft.shape[0],1)), 0*aft))
        a3 = np.hstack((0*afs, 0*afs, np.zeros((afs.shape[0],1)), afs))
        flow_names3 = populate_constraint_names(["no_in_source_sys"], edges_keys=s3_edges)
        flow_names.extend(flow_names3)
        Afeas = np.vstack((a1, a3))

    bfeas = np.zeros((Afeas.shape[0],1))
    assert Afeas.shape[0] == bfeas.shape[0]
    return Afeas, bfeas, flow_names

# No out sink
def no_out_sink(edges_keys, src, int, sink, projection=False):
    flow_names = []

    ne = len(list(edges_keys.keys())) # number of edges
    out_t1_edge_ind = [k for k, v in edges_keys.items() if v[0] in int]
    out_t3_edge_ind = [k for k, v in edges_keys.items() if v[0] in sink]

    aft = np.zeros((len(out_t1_edge_ind), ne))
    afs = np.zeros((len(out_t3_edge_ind), ne))

    t1_edges = dict()
    t3_edges = dict()

    for i, k in enumerate(out_t1_edge_ind):
        t1_edges[k] = edges_keys[k]
        aft[i, k] = 1

    for i, k in enumerate(out_t3_edge_ind):
        t3_edges[k] = edges_keys[k]
        afs[i, k] = 1

    flow_names1 = populate_constraint_names(["no_out_sink1"], edges_keys=t1_edges)
    flow_names.extend(flow_names1)
    if projection:
        Afeas = np.hstack((aft, 0*aft, np.zeros((aft.shape[0],1))))
    else:
        a1 = np.hstack((aft, 0*aft, np.zeros((aft.shape[0],1)), 0*aft))
        a3 = np.hstack((0*afs, 0*afs, np.zeros((afs.shape[0],1)), afs))
        flow_names3 = populate_constraint_names(["no_out_sink3"], edges_keys=t3_edges)
        flow_names.extend(flow_names3)
        Afeas = np.vstack((a1, a3))

    bfeas = np.zeros((Afeas.shape[0],1))
    assert Afeas.shape[0] == bfeas.shape[0]
    return Afeas, bfeas, flow_names

# No in/out intermediate
def no_in_out_interm(edges_keys, src, int, sink, projection=False):
    flow_names = []

    ne = len(list(edges_keys.keys())) # number of edges
    in_int_edge_ind = [k for k, v in edges_keys.items() if v[1]==int]
    out_int_edge_ind = [k for k, v in edges_keys.items() if v[0]==int]

    af3_in = np.zeros((len(in_int_edge_ind), ne))
    af3_out = np.zeros((len(out_int_edge_ind), ne))

    in_edges = dict()
    out_edges = dict()

    for i, k in enumerate(in_int_edge_ind):
        in_edges[k] = edges_keys[k]
        af3_in[i, k] = 1

    for i, k in enumerate(out_int_edge_ind):
        out_edges[k] = edges_keys[k]
        af3_out[i, k] = 1

    flow_names1 = populate_constraint_names(["no_in_interm"], edges_keys=in_edges)
    flow_names2 = populate_constraint_names(["no_out_interm"], edges_keys=out_edges)
    flow_names.extend(flow_names1)
    flow_names.extend(flow_names2)

    a3_in = np.hstack((0*af3_in, 0*af3_in, np.zeros((af3_in.shape[0],1)), af3_in))
    a3_out = np.hstack((0*af3_out, 0*af3_out, np.zeros((af3_out.shape[0],1)), af3_out))

    Afeas = np.vstack((a3_in, a3_out))
    bfeas = np.zeros((Afeas.shape[0],1))
    assert Afeas.shape[0] == bfeas.shape[0]
    return Afeas, bfeas, flow_names

# Equality constraint:
def eq_aux_constraint(edges_keys, projection=False):
    ne = len(list(edges_keys.keys())) # number of edges
    eq_names = []
    eq_block = np.array([[1,-1]])

    Aeq_t = np.zeros((ne-1, ne))
    beq = np.zeros((ne-1,1))
    # Take care of t
    for k in range(ne-1):
        At = np.zeros((1,ne))
        At[0,k:k+2] = eq_block
        Aeq_t[k] = At.copy()
    # pdb.set_trace()
    # Organize larger matrices:
    zblock = 0*Aeq_t
    eq_names = populate_constraint_names(["eq"], edges_keys=edges_keys)
    if projection:
        Aeq = np.hstack((zblock, zblock, zblock, Aeq_t))
    else:
        Aeq = np.hstack((zblock, zblock, zblock, Aeq_t, zblock))
    assert Aeq.shape[0] == beq.shape[0]
    return Aeq, beq, eq_names

# Collecting all constraints together as g(x,y) = A[x;y] - b>=0
def all_constraints(edges_keys, nodes_keys, src, int, sink):
    A_cap, b_cap, cap_names = capacity_constraint(edges_keys)
    A_cons, b_cons, cons_names = conservation_constraint(nodes_keys, edges_keys, src, int, sink)
    A_cut, b_cut, cut_names = cut_constraint(edges_keys)

    A_no_in_src, b_no_in_src, no_in_src_names = no_in_source(edges_keys, src, int, sink)
    A_no_out_sink, b_no_out_sink, no_out_sink_names = no_out_sink(edges_keys, src, int, sink)
    A_no_in_out_interm, b_no_in_out_interm, no_in_out_interm_names = no_in_out_interm(edges_keys, src, int, sink)

    Aeq = np.vstack((A_cons, A_no_in_src, A_no_out_sink, A_no_in_out_interm))
    beq = np.vstack((b_cons, b_no_in_src, b_no_out_sink, b_no_in_out_interm))
    eq_cons_names = [*cons_names, *no_in_src_names, *no_out_sink_names, *no_in_out_interm_names]
    try:
        assert Aeq.shape[0] == len(eq_cons_names)
    except:
        pdb.set_trace()
    Aineq = np.vstack((A_cap, A_cut))
    bineq = np.vstack((b_cap, b_cut))
    ineq_cons_names = [*cap_names, *cut_names]
    assert Aineq.shape[0] == len(ineq_cons_names)
    return Aeq, beq, eq_cons_names, Aineq, bineq, ineq_cons_names

# Collecting projection constraints together as g(x,y) = A[x;y] - b>=0
# Difficulty in projection constraints getting satisfied
def outer_player_constraints(edges_keys, nodes_keys, src, int, sink):
    A_nonneg, b_nonneg, nonneg_names = nonneg_constraint(edges_keys, projection=True)
    A_cap, b_cap, cap_names = capacity_constraint(edges_keys, projection=True)
    A_cons, b_cons, cons_names = proj_conservation_constraint(nodes_keys, edges_keys, src, int, sink)
    # A_eq, b_eq, eq_names = eq_aux_constraint(edges_keys, projection=True)
    A_cut, b_cut, cut_names = cut_constraint(edges_keys, projection=True)
    A_no_in_src, b_no_in_src, no_in_src_names = no_in_source(edges_keys, src, int, sink, projection=True)
    A_no_out_sink, b_no_out_sink, no_out_sink_names = no_out_sink(edges_keys, src, int, sink, projection=True)
    
    Aeq = np.vstack((A_cons, A_no_in_src, A_no_out_sink))
    beq = np.vstack((b_cons, b_no_in_src, b_no_out_sink))
    eq_cons_names = [*cons_names, *no_in_src_names, *no_out_sink_names]

    Aineq = np.vstack((A_nonneg, A_cap, A_cut))
    bineq = np.vstack((b_nonneg, b_cap, b_cut))
    ineq_cons_names = [*nonneg_names, *cap_names, *cut_names]
    return Aeq, beq, eq_cons_names, Aineq, bineq, ineq_cons_names


# Matching edges:
def match_edges(edges_keys, ne, flow_dict):
    flow_init = np.zeros((ne,1))
    for k, edge in edges_keys.items():
        flow_init[k,0] = flow_dict[edge[0]][edge[1]] # Parsing the flow dict
    return flow_init

# Projection constraints:
def proj_constraints_box_only(edges_keys, nodes_keys, src, int, sink):
    A_cap, b_cap, cap_names = capacity_constraint(edges_keys, projection=True)
    A_cons, b_cons, cons_names = proj_conservation_constraint(nodes_keys, edges_keys, src, int, sink)
    # A_eq, b_eq, eq_names = eq_aux_constraint(edges_keys, projection=True)
    A_cut, b_cut, cut_names = cut_constraint(edges_keys, projection=True)
    A_flow, b_flow, flow_names = min_flow_constraint(edges_keys, src, int, sink, projection=True)
    A_no_in_src, b_no_in_src, no_in_src_names = no_in_source(edges_keys, src, int, sink, projection=True)
    A_no_out_sink, b_no_out_sink, no_out_sink_names = no_out_sink(edges_keys, src, int, sink, projection=True)
    # A = np.vstack((A_feas, A_cap))
    # b = np.vstack((b_feas, b_cap))
    Aeq = np.vstack((A_cons, A_no_in_src, A_no_out_sink))
    beq = np.vstack((b_cons, b_no_in_src, b_no_out_sink))
    eq_cons_names = [*cons_names, *no_in_src_names, *no_out_sink_names]

    Aineq = np.vstack((A_cap, A_cut,  A_flow))
    bineq = np.vstack((b_cap, b_cut, b_flow))
    ineq_cons_names = [*cap_names, *cut_names, *flow_names]
    return Aeq, beq, eq_cons_names, Aineq, bineq, ineq_cons_names

# Get candidate flows :
def compute_flows(Gnx, src, int, sink):
    source = src
    inter = int
    target = sink
    if isinstance(src, list):
        Gnx.add_nodes_from(["Src"])
        for si in src:
            Gnx.add_edge("Src", si)
        source = "Src"

    if isinstance(int, list):
        Gnx.add_nodes_from(["Int"])
        for si in int:
            Gnx.add_edge("Int", si)
            Gnx.add_edge(si, "Int")
        inter = "Int"

    if isinstance(sink, list):
        Gnx.add_nodes_from(["Sink"])
        for si in sink:
            Gnx.add_edge(si, "Sink")
        target = "Sink"

    f1e_value, f1e_dict = nx.maximum_flow(Gnx, source, inter)
    f2e_value, f2e_dict = nx.maximum_flow(Gnx, inter, target)
    f3e_value, f3e_dict = nx.maximum_flow(Gnx, source, target)
    pdb.set_trace()
    dict1, dict2, dict3 = dict(f1e_dict), dict(f2e_dict), dict(f3e_dict)
    # for d in [dict1, dict2, dict3]:
    #     for k, v in d.items():
    #         pdb.set_trace()
    #         if "Src" == k[0] or "Src" == k[1]:
    #             del d[k]
    #         if "Int" == k[0] or "Int" == k[1]:
    #             del d[k]
    #         if "Sink" == k[1] or "Sink" == k[1]:
    #             del d[k]
    return f1e_value, f2e_value, f3e_value, dict1, dict2, dict3

# Function to get a candidate initial condition:
def get_candidate_flows(G, edges_keys, src, int, sink):
    ne = len(list(edges_keys.keys()))
    Gnx = nx.DiGraph()
    for edge in G.edges():
        Gnx.add_edge(*edge, capacity=1.0)

    f1e_value, f2e_value, f3e_value, f1e_dict, f2e_dict, f3e_dict = compute_flows(Gnx, src, int, sink)

    F_init = min(f1e_value, f2e_value)
    try:
        assert F_init > 0.0
    except:
        pdb.set_trace()
    f1e_init = match_edges(edges_keys, ne, f1e_dict) # Match flow values to edges keys consistent with the indices used in our optimization.
    f2e_init = match_edges(edges_keys, ne, f2e_dict)
    f3e_init = match_edges(edges_keys, ne, f3e_dict)
    tfac = 1.0/F_init
    t_init = tfac * np.ones((ne,1))
    zero_cuts = np.zeros((ne,1))
    x0 = np.vstack((f1e_init*tfac, f2e_init*tfac, zero_cuts, tfac))
    return x0, f3e_init*tfac

# Adjust max flows for cuts:
def adjust_flows_for_cuts(G, init_edge_cuts, src, int, sink, edges_keys):
    '''
    Same function as above but finds the max flow when the network has some cuts initially
    '''
    ne = len(list(edges_keys.keys()))
    cuts = np.zeros((ne,1))
    Gnx = nx.DiGraph()
    for edge in G.edges():
        if edge in init_edge_cuts:
            Gnx.add_edge(*edge, capacity=1.0 - 0.7)
        else:
            Gnx.add_edge(*edge, capacity=1.0)
    f1e_value, f1e_dict = nx.maximum_flow(Gnx, src, int)
    f2e_value, f2e_dict = nx.maximum_flow(Gnx, int, sink)
    f3e_value, f3e_dict = nx.maximum_flow(Gnx, src, sink)
    F_init = min(f1e_value, f2e_value)
    assert F_init > 0.0
    f1e_init = match_edges(edges_keys, ne, f1e_dict) # Match flow values to edges keys consistent with the indices used in our optimization.
    f2e_init = match_edges(edges_keys, ne, f2e_dict)
    f3e_init = match_edges(edges_keys, ne, f3e_dict)
    tfac = 1.0/F_init
    t_init = tfac * np.ones((ne,1))
    x0 = np.vstack((f1e_init*tfac, f2e_init*tfac, cuts, tfac))
    return x0

def plot_matrix(M, fn):
    fn = os.getcwd() + "/" + fn
    plt.matshow(M)
    plt.show()
    plt.savefig(fn)

def parse_solution(xtraj, ytraj, G, edges_keys, nodes_keys):
    ne = len(edges_keys)
    f1_e_hist = [dict() for k in range(len(xtraj))]
    f2_e_hist = [dict() for k in range(len(xtraj))]
    f3_e_hist = [dict() for k in range(len(xtraj))]
    d_e_hist = [dict() for k in range(len(xtraj))]
    F_hist = [0 for k in range(len(xtraj))]
    for t in range(len(xtraj)):
        try:
            x = xtraj[t]
            y = ytraj[t]
            F_hist[t] = 1/x[-1]
            for idx, val in edges_keys.items():
                f1_e_hist[t].update({val: x[idx]*F_hist[t]})
                f2_e_hist[t].update({val: x[ne + idx]*F_hist[t]})
                d_e_hist[t].update({val: x[2*ne + idx]*F_hist[t]})
                f3_e_hist[t].update({val: y[val]*F_hist[t]})
        except:
            pdb.set_trace()
    return f1_e_hist, f2_e_hist, f3_e_hist, d_e_hist, F_hist
