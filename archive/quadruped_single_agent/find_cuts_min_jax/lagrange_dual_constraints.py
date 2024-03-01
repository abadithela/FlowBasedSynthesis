import numpy as np
from ipdb import set_trace as st
from scipy import sparse as sp
from find_cuts import setup_nodes_and_edges, get_graph

# Lagrange dual constraints:
def lagrange_dual_nonneg(edges_keys, nodes_keys, src, int, sink):
    ne = len(list(edges_keys.keys())) # number of edges
    nv = len(list(nodes_keys.keys()))

    A_lag = np.identity(ne+nv)
    b_lag = np.zeros((ne+nv,1))

    return A_lag, b_lag           

def lamd_zero_interm(edges_keys, nodes_keys, src, int, sink):
    ne = len(list(edges_keys.keys())) # number of edges
    nv = len(list(nodes_keys.keys()))

    in_int_edge_ind = [k for k, v in edges_keys.items() if v[1]==int]
    out_int_edge_ind = [k for k, v in edges_keys.items() if v[0]==int]

    lamd_in = np.zeros((len(in_int_edge_ind), ne))
    lamd_out = np.zeros((len(out_int_edge_ind), ne))
    mu_zeros_in = np.zeros((len(in_int_edge_ind), nv))
    mu_zeros_out = np.zeros((len(out_int_edge_ind), nv))

    for i, k in enumerate(in_int_edge_ind):
        lamd_in[i, k] = 1
    
    for i, k in enumerate(out_int_edge_ind):
        lamd_out[i, k] = 1

    A_lag = np.vstack((np.hstack((lamd_in, mu_zeros_in)), np.hstack((lamd_out, mu_zeros_out))))
    b_lag = np.zeros((len(in_int_edge_ind) + len(out_int_edge_ind),1))
    assert A_lag.shape[0] == b_lag.shape[0]
    return A_lag, b_lag

def partition_constraints(edges_keys, nodes_keys, src, int, sink):
    ne = len(list(edges_keys.keys())) # number of edges
    nv = len(list(nodes_keys.keys()))

    ncomb = len(src)*len(sink)
    lamd_zeros = np.zeros((ncomb, ne))
    mu = np.zeros((ncomb, nv))

    src_sink_comb = [(i,j) for i in src for j in sink]
    assert ncomb == len(src_sink_comb)
    for k, elem in enumerate(src_sink_comb):
        i,j = elem
        mu[k, i] = 1
        mu[k, j] = -1

    A_lag = np.hstack((lamd_zeros, mu))
    b_lag = np.ones((ncomb,1))

    assert A_lag.shape[0] == b_lag.shape[0]
    return A_lag, b_lag

def lamd_mu_coupled_constraints(edges_keys, nodes_keys, src, int, sink):
    ne = len(list(edges_keys.keys())) # number of edges
    nv = len(list(nodes_keys.keys()))

    lamd = np.zeros((ne, ne))
    mu = np.zeros((ne, nv))

    for k, edge in edges_keys.items():
        i,j = edge
        mu[k, i] = -1
        mu[k, j] = 1
        lamd[k, k] = 1

    A_lag = np.hstack((lamd, mu))
    b_lag = np.zeros((ne,1))

    assert A_lag.shape[0] == b_lag.shape[0]
    return A_lag, b_lag

def lagrange_dual_constraints(edges_keys, nodes_keys, src, int, sink):
    An, bn = lagrange_dual_nonneg(edges_keys, nodes_keys, src, int, sink)
    Az, bz = lamd_zero_interm(edges_keys, nodes_keys, src, int, sink)
    Ap, bp = partition_constraints(edges_keys, nodes_keys, src, int, sink)
    Ac, bc = lamd_mu_coupled_constraints(edges_keys, nodes_keys, src, int, sink)

    # Separating inequality and equality constraints
    A_lag_ineq = np.vstack((An, Ap, Ac))
    b_lag_ineq = np.vstack((bn, bp, bc))
    return A_lag_ineq, b_lag_ineq, Az, bz
    