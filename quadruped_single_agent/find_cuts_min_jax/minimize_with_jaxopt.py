from typing import NamedTuple
import optax
import jax
from jax import numpy as jnp
import jaxopt

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
    f, G, h, x0, num_iters=1000, lr=1e-2, name="sgd", verbose=True
):
    """
    Minimizes a function using an optimizer.

    Parameters:
    -----------
    f: Callable
        The function to be minimized.
    x0: Any
        The initial value of the parameters.
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
        hyperparams=(jnp.zeros((num_vars, num_vars)), jnp.zeros(num_vars), G, h),
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

def minimize(
    f, x0, proj=lambda x: x, num_iters=1000, lr=1e-2, name="adam", verbose=True
):
    """
    Minimizes a function using an optimizer.

    Parameters:
    -----------
    f: Callable
        The function to be minimized.
    x0: Any
        The initial value of the parameters.
    proj: Callable
        The projection function. Default is the identity function.
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

    # Define the update function
    @jax.jit
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


def maximize(
    f, x0, proj=lambda x: x, num_iters=1000, lr=1e-2, name="adam", verbose=True
):
    """
    Maximizes a function using an optimizer.

    Parameters:
    -----------
    f: Callable
        The function to be maximized.
    x0: Any
        The initial value of the parameters.
    proj: Callable
        The projection function. Default is the identity function.
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
    return minimize(
        lambda x: -f(x),
        x0,
        proj=lambda x: x,
        num_iters=1000,
        lr=1e-2,
        name="adam",
        verbose=True,
    )

if __name__ == "__main__":
    num_vars = 10
    f = lambda x,y: jnp.linalg.norm(x) + jnp.linalg.norm(y)

    G = jnp.identity(num_vars) # Matrix of coonstraint coefficients
    h = jnp.ones(num_vars) # Vector of constraint biases

    x0 = jax.random.uniform(jax.random.PRNGKey(42), shape = (num_vars, ))

    minimize_on_polyhedron(
        f, G, h, x0, num_iters=1000, lr=1e-2, name="sgd", verbose=True
    )
