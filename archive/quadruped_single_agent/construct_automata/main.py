"""
Script to construct and test products
"""
import sys
sys.path.append('..')
sys.path.append('../..')
import os
# sys.path.append("/Users/apurvabadithela/software/VisualizeAutomata/patrolling_car")
import pdb

try:
    from transition_system import ProductTransys, Transys
    import product_automata_quadruped as product_automata # specific to example
    from automaton import Automaton
    from flow.constraints.products import Product # important for plotting
except:
    from construct_automata.transition_system import ProductTransys, Transys
    import construct_automata.product_automata_quadruped as product_automata # specific to example
    from construct_automata.automaton import Automaton
    from flow_constraints.products import Product # important for plotting

def construct_automata_async(AP_set=None):
    Q, qinit, AP, tau, Acc = example_automata.async_product(state_str="q")
    for ap in AP:
        assert ap in AP_set
    aut = Automata(Q, qinit, AP_set, tau, Acc)
    return aut

def construct_system():
    """
    Construct system from maze.txt
    """
    mazefile = "../graph/mazefiles/maze.txt"
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
    aut.to_graph()
    return aut

def get_virtual_product_graphs(mazefile):
    system = ProductTransys()
    system.construct_sys(mazefile)
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

def construct_system_quadruped():
    """
    Construct system from maze.txt
    """
    mazefile = "../simulation/maze.txt"
    system = ProductTransys()
    system.construct_sys(mazefile)
    return system

def quad_test_sync():
    system = construct_system_quadruped()

    b_pi = construct_sync_automaton_quad_ex(AP_set = system.AP)
    b_pi.save_plot("imgs/prod_aut")
    virtual = sync_prod(system, b_pi)
    if not os.path.exists("imgs"):
        os.makedirs("imgs")
    system.save_plot("imgs/transys")
    # aut.save_plot("imgs/sync_spec_product/specification_product")
    virtual.save_plot("imgs/virtual")

    initial = {'red': virtual.I}

    virtual.highlight_states(initial, "imgs/virtual_initial")
    virtual.prune_unreachable_nodes("imgs/reachable")

    # load just system automaton and take sync product
    Q, qinit, AP, tau, Acc = product_automata.get_b_sys(state_str="q")
    b_sys = Automaton(Q, qinit, system.AP, tau, Acc)

    # Printing automaton:
    virtual_sys = sync_prod(system, b_sys)
    virtual_sys.save_plot("imgs/virtual_sys")
    virtual_sys.prune_unreachable_nodes("imgs/reachable_sys")
    initial_sys = {'red': virtual_sys.I}
    virtual_sys.highlight_states(initial_sys, "imgs/virtual_initial")
    
    # pdb.set_trace()
    return virtual, system, b_pi, virtual_sys

if __name__ == "__main__":
    # quad_test_async()
    quad_test_sync()
    # pdb.set_trace()
