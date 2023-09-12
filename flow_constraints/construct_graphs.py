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

def construct_system():
    """
    Construct system from maze.txt
    """
    mazefile = "maze.txt"
    system = ProductTransys()
    system.construct_sys(mazefile)
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

def sys_test_sync():
    system = construct_system()

    b_pi = construct_sync_automaton_quad_ex(AP_set = system.AP)
    virtual = sync_prod(system, b_pi)
    if not os.path.exists("imgs"):
        os.makedirs("imgs")
    system.save_plot("imgs/transys")
    virtual.save_plot("imgs/virtual")

    initial = {'red': virtual.I}

    virtual.highlight_states(initial, "imgs/virtual_initial")
    virtual.prune_unreachable_nodes("imgs/reachable")

    # load just system automaton and take sync product
    Q, qinit, AP, tau, Acc = product_automata.get_b_sys(state_str="q")
    b_sys = Automaton(Q, qinit, system.AP, tau, Acc)
    virtual_sys = sync_prod(system, b_sys)
    virtual_sys.save_plot("imgs/virtual_sys")
    virtual_sys.prune_unreachable_nodes("imgs/reachable_sys")
    initial_sys = {'red': virtual_sys.I}
    virtual_sys.highlight_states(initial_sys, "imgs/virtual_initial")

    return virtual, system, b_pi, virtual_sys

if __name__ == "__main__":
    # quad_test_async()
    sys_test_sync()
    # pdb.set_trace()
