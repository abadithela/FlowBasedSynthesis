"""
Script to construct and test products
"""
import sys
import os
# sys.path.append("/Users/apurvabadithela/software/VisualizeAutomata/patrolling_car")
import pdb
try:
    from transition_system import ProductTransys, Transys
    import product_automata_runner_blocker as product_automata
    from automaton import Automaton
    from products import Product
except:
    from construct_automata.transition_system import ProductTransys, Transys
    import construct_automata.product_automata_runner_blocker as product_automata
    from construct_automata.automaton import Automaton
    from construct_automata.products import Product

# import product_automata_runner_blocker as product_automata
# from automaton import Automaton
# import plotting
# from products import Product

def sync_prod(system, aut):
    sys_prod = Product(system, aut)
    sys_prod.construct_labels()
    sys_prod.construct_transitions()
    return sys_prod

def construct_sync_automaton_runner_blocker(AP_set = None):
    Q, qinit, AP, tau, Acc = product_automata.load_sync_product(state_str="q")
    for ap in AP:
        assert ap in AP_set
    aut = Automaton(Q, qinit, AP_set, tau, Acc)
    return aut

def construct_system_runner_blocker():
    """
    Construct system from maze.txt
    """
    system = ProductTransys()
    system.construct_sys()
    return system

def runner_blocker_test_sync():
    ts = construct_system_runner_blocker()
    prod_ba = construct_sync_automaton_runner_blocker(AP_set = ts.AP)
    virtual = sync_prod(ts, prod_ba)
    if not os.path.exists("imgs"):
        os.makedirs("imgs")
    ts.save_plot("imgs/product_transys")
    # aut.save_plot("imgs/sync_spec_product/specification_product")
    virtual.save_plot("imgs/sync_prod_graph")
    initial = {'red': virtual.I}
    virtual.highlight_states(initial, "imgs/sync_prod_graph")
    virtual.prune_unreachable_nodes("imgs/sync_spec_reachable")

    #
    # pdb.set_trace()
    return virtual, ts, prod_ba

if __name__ == "__main__":
    # quad_test_async()
    prod_graph, system, aut = runner_blocker_test_sync()
    pdb.set_trace()
