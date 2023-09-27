from typing import NamedTuple
import optax
import jax
from jax import numpy as jnp
import jaxopt
# from minimize_with_jaxopt import init_optimiser, minimize_on_polyhedron
from outer_player_constraints import *
from construct_automata.main import quad_test_sync
from inner_min import solve_inner_min
from find_cuts import setup_nodes_and_edges, get_graph
from lagrange_dual_constraints import lagrange_dual_constraints
from initialize_max_flow import initialize_max_flow
import pdb

gamma = 0.999
ne = 0
nv = 0

class TrainState(NamedTuple):
    """
    A class that stores the state of the training.

    Attributes:
    -----------
    optimizer: optax.TransformUpdateFn
        The optimizer function used for updating the parameters.
    state: optax.OptState
        The optimizer state.
    """

    update: optax.TransformUpdateFn
    state: optax.OptState


def init_optimiser(lr, params, name="adam", **kwargs):
    """
    Initializes an optimizer.

    Parameters:
    -----------
    lr: float
        The learning rate.
    params: Any
        The parameters to be optimized.
    name: str
        The name of the optimizer. Default is "adam".

    Returns:
    --------
    TrainState
        The state of the training.
    """
    if name == "sgd":
        optimizer = optax.sgd(lr, **kwargs)
    elif name == "adam":
        optimizer = optax.adam(lr, **kwargs)
    elif name == "rmsprop":
        optimizer = optax.rmsprop(lr, **kwargs)
    elif name == "optimistic_gradient_descent":
        optimizer = optax.optimistic_gradient_descent(lr, **kwargs)
    else:
        raise ValueError(f"Invalid optimizer name: {name}")

    opt_init, opt_update = optimizer
    opt_state = opt_init(params)
    return TrainState(opt_update, opt_state)


def minimize_on_polyhedron(
    f, A, b, G, h, x0, y0, num_iters=1000, lr=1e-2, name="sgd", verbose=True
):
    """
    Minimizes a function using an optimizer.

    Parameters:
    -----------
    f: Callable
        The function to be minimized.
    x0: Any
        The initial value of outer player parameters.
    y0: Any
        The initial value of lagrange parameters.
    A: jnp.array
        Matrix of polyhedron constraints s.t. Ax = b
    b: jnp.array
        Vector of polyhedron constraints s.t.  Ax = b
    G: jnp.array
        Matrix of polyhedron constraints s.t. Gx <= h
    h: jnp.array
        Vector of polyhedron constraints s.t.  Gx <= h
    num_iters: int
        The number of iterations. Default is 1000.
    lr: float
        The learning rate. Default is 1e-2.
    name: str
        The name of the optimizer. Default is "adam".
    verbose: bool
        Whether to print the loss at each iteration. Default is True.

    Returns:
    --------
    Any
        The optimized parameters.
    """
    # Define the gradient function
    grad_f = jax.grad(f)

    # Define the optimizer
    opt_update, opt_state = init_optimiser(lr, x0, name)

    num_vars = x0.shape[0]
    proj = lambda x: jaxopt.projection.projection_polyhedron(
        x,
        hyperparams=(A,b, G, h),
        check_feasible=False,
    )
    # Equality constraints
    # proj = lambda x: jaxopt.projection.projection_polyhedron(
    #     x,
    #     hyperparams=(A, b, G, h),
    #     check_feasible=False,
    # )

    # Define the update function
    @jax.jit # Makes code run 100X faster
    def update(x, opt_state):
        grads = grad_f(x)
        updates, new_state = opt_update(grads, opt_state, x)
        new_x = optax.apply_updates(x, updates)
        new_x = proj(new_x)
        return new_x, new_state

    # Minimize the function
    x = x0
    for i in range(num_iters):
        if verbose:
            if i % 100 == 0:
                print(f"Iteration {i}, loss {f(x):.5f}")
        x, opt_state = update(x, opt_state)

    return x

def initialize():
    virtual, system, b_pi, virtual_sys = quad_test_sync()
    GD, S = setup_nodes_and_edges(virtual, virtual_sys, b_pi)
    G = get_graph(GD.nodes, GD.edges)
    # remove self loops
    edges = list(G.edges())
    global ne 
    ne = len(edges)
    global nv 
    nv = len(GD.nodes)
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
    return x, y, G, GD, nodes_keys, edges_keys

def parse_solution(xtraj,ytraj):
    # todo: fix
    f1_e_hist = [dict() for k in range(len(xtraj))]
    f2_e_hist = [dict() for k in range(len(xtraj))]
    f3_e_hist = [dict() for k in range(len(xtraj))]
    d_e_hist = [dict() for k in range(len(xtraj))]
    F_hist = [0 for k in range(len(xtraj))]
    for t in range(len(xtraj)):
        x = xtraj[t]
        y = ytraj[t]
        F_hist[t] = 1/x[-1]
        for idx, val in edges_keys.items():
            f1_e_hist[t].update({val: x[idx]*F_hist[t]})
            f2_e_hist[t].update({val: x[ne + idx]*F_hist[t]})
            d_e_hist[t].update({val: x[2*ne + idx]*F_hist[t]})
            f3_e_hist[t].update({val: y[val]*F_hist[t]})
    return f1_e_hist, f2_e_hist, f3_e_hist, d_e_hist, F_hist

def process_nodes(init, intermed, goal):
    if isinstance(init, list):
        src = init
    else:
        src = [init]
    if isinstance(intermed, list):
        int = intermed
    else:
        int = [intermed]
    if isinstance(goal, list):
        sink = goal
    else:
        sink = [goal]
    return src, int, sink

def f(x):
    '''
    x: (ft, d, t, lambda, mu) \in R^(3|E| + |V| + 1)
    '''
    ft = x[0:ne]
    d = x[ne+1:2*ne]
    t = x[2*ne]
    # lamd = x[2*ne+1, 3*ne]
    # mu = x[3*ne:]
    second_term = 0
    for k in range(ne):
        second_term += (t - d[k])
    obj = (1-gamma)*t + gamma*jnp.dot(lamd, tvec - d)
    return obj

if __name__ == "__main__":
    x, y, G, GD, nodes_keys, edges_keys = initialize()
    src, int, sink = process_nodes(GD.init, GD.int, GD.sink)
    pdb.set_trace()
    Ax_eq, bx_eq, eq_cons_names, Ax_ineq, bx_ineq, ineq_cons_names = outer_player_constraints(edges_keys, nodes_keys, src, int, sink)
    A_lag_ineq, b_lag_ineq, A_lag_eq, b_lag_eq = lagrange_dual_constraints(edges_keys, nodes_keys, src, int, sink)

    # Aeq = jnp.array(Aeq). Check array type for jax vs. numpy.
    # Concatenate the vector: [f,d,t,lamd, mu]
    # Inequality constraints:
    Ax_ineq_shape = Ax_ineq.shape
    Alag_ineq_shape = A_lag_ineq.shape
    A_ineq_first_block_row = jnp.hstack((Ax_ineq, jnp.zeros((Ax_ineq_shape[0], Alag_ineq_shape[1]))))
    A_ineq_second_block_row = jnp.hstack((jnp.zeros((Alag_ineq_shape[0], Ax_ineq_shape[1])), A_lag_ineq))
    Gmat = -1*jnp.vstack((A_ineq_first_block_row, A_ineq_second_block_row))
    hmat = -1*jnp.vstack((bx_ineq, b_lag_ineq))

    # Equality constraints:
    Ax_eq_shape = Ax_eq.shape
    Alag_eq_shape = A_lag_eq.shape
    A_eq_first_block_row = jnp.hstack((Ax_eq, jnp.zeros((Ax_eq_shape[0], Alag_eq_shape[1]))))
    A_eq_second_block_row = jnp.hstack((jnp.zeros((Alag_eq_shape[0], Ax_eq_shape[1])), A_lag_eq))
    Amat = jnp.vstack((A_eq_first_block_row, A_eq_second_block_row))
    bmat = jnp.vstack((bx_eq, b_lag_eq))

    # To define: x0
    ft_init, fs_init, t_lower = initialize_max_flow(G, src, int, sink)
    d_init = np.zeros((ne,1))
    lam, mu = solve_inner_min(GD) 
    x0 = jnp.vstack((ft_init, d_init, t_lower, lam, mu))
    # Minimize:
    minimize_on_polyhedron(
        f, Amat, bmat, Gmat, hmat, x0, y0, num_iters=1000, lr=1e-2, name="adam", verbose=True
    )
    pdb.set_trace()