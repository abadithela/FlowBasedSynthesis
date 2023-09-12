"""
Script to construct and test products
"""
import sys
import os
import pdb

import product_automata_small_example as product_automata

try:
    from transition_system import ProductTransys, Transys
    from automaton import Automaton
    from products import Product
except:
    from flow_constraints.transition_system import ProductTransys, Transys
    from flow_constraints.automaton import Automaton
    from flow_constraints.products import Product

def construct_system(ints, goals):
    """
    Construct system from maze.txt
    """
    mazefile = "maze.txt"
    system = ProductTransys()
    system.construct_sys(mazefile, ints, goals)
    return system

def sync_prod(system, aut):
    sys_prod = Product(system, aut)
    sys_prod.construct_labels()
    sys_prod.construct_transitions()
    return sys_prod

def construct_sync_automaton_quad_ex(AP_set = None):
    Q, qinit, AP, tau, Acc = product_automata.sync_product(state_str="q")
    for ap in AP:
        assert ap in AP_set
    aut = Automaton(Q, qinit, AP_set, tau, Acc)
    return aut

def sys_test_sync(ints, goals):
    system = construct_system(ints, goals)

    b_pi = construct_sync_automaton_quad_ex(AP_set = system.AP)
    virtual = sync_prod(system, b_pi)
    if not os.path.exists("imgs"):
        os.makedirs("imgs")
    virtual.plot_graph("imgs/virtual")

    # load just system automaton and take sync product
    Q, qinit, AP, tau, Acc = product_automata.get_b_sys(state_str="q")
    b_sys = Automaton(Q, qinit, system.AP, tau, Acc)
    virtual_sys = sync_prod(system, b_sys)
    virtual_sys.plot_graph("imgs/virtual_sys")

    return virtual, system, b_pi, virtual_sys

if __name__ == "__main__":
    # quad_test_async()
    sys_test_sync()
    # pdb.set_trace()
