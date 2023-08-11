"""
Script to construct and test products
"""
import sys
import os
# sys.path.append("/Users/apurvabadithela/software/VisualizeAutomata/patrolling_car")
import pdb
from transition_system import ProductTransys, Transys
import product_automata_quadruped as product_automata
from automaton import Automaton
# import plotting
from products import Product

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

def async_example():
    system = construct_system()
    aut = construct_automata_async(AP_set = system.AP)
    prod_graph = sync_prod(system, aut)
    if not os.path.exists("imgs/example_automata/"):
        os.makedirs("imgs/example_automata")
    prod_graph.save_plot("imgs/example_automata/prod_graph")

def construct_sync_automaton_quad_ex(AP_set = None):
    Q, qinit, AP, tau, Acc = product_automata.sync_product(state_str="q")
    for ap in AP:
        assert ap in AP_set
    aut = Automaton(Q, qinit, AP_set, tau, Acc)
    return aut

def construct_async_automaton_quad_ex(AP_set = None):
    Q, qinit, AP, tau, Acc = product_automata.async_product(state_str="q")
    for ap in AP:
        assert ap in AP_set
    aut = Automaton(Q, qinit, AP_set, tau, Acc)
    return aut

def construct_system_quadruped():
    """
    Construct system from maze.txt
    """
    mazefile = "../simulation/maze.txt"
    system = ProductTransys()
    system.construct_sys(mazefile)
    return system

def quad_test_async():
    system = construct_system_quadruped()
    aut = construct_async_automaton_quad_ex(AP_set = system.AP)
    prod_graph = sync_prod(system, aut)
    if not os.path.exists("imgs/async_spec_product"):
        os.makedirs("imgs/async_spec_product")
    system.save_plot("imgs/async_spec_product/product_transys")
    # aut.save_plot("imgs/async_spec_product/specification_product")
    prod_graph.save_plot("imgs/async_spec_product/prod_graph")
    pdb.set_trace()

def quad_test_sync():
    system = construct_system_quadruped()
    aut = construct_sync_automaton_quad_ex(AP_set = system.AP)
    prod_graph = sync_prod(system, aut)
    if not os.path.exists("imgs/sync_spec_product"):
        os.makedirs("imgs/sync_spec_product")
    system.save_plot("imgs/sync_spec_product/product_transys")
    # aut.save_plot("imgs/sync_spec_product/specification_product")
    prod_graph.save_plot("imgs/sync_spec_product/prod_graph")
    # state_list = []
    # for state in prod_graph.plt_sink_int:
    #     state_list.append(str(state))
    initial = {'red': prod_graph.I}
    # highlight_states={'red': [(((0, 0), (0, 1), 's'), 'q0'), (((0, 0), (1, 1), 's'), 'q0'), (((0, 0), (2, 1), 's'), 'q0')],
    #                   'magenta': [(((0, 0), (0, 1), 's'), 'q1'), (((0, 0), (1, 1), 's'), 'q1'), (((0, 0), (2, 1), 's'), 'q1')],
    #                   'cyan': [(((0, 0), (0, 1), 's'), 'q2'), (((0, 0), (1, 1), 's'), 'q2'), (((0, 0), (2, 1), 's'), 'q2')],
    #                   'green': [(((0, 0), (0, 1), 's'), 'q3'), (((0, 0), (1, 1), 's'), 'q3'), (((0, 0), (2, 1), 's'), 'q3')]
    #                   }
    prod_graph.highlight_states(initial, "imgs/sync_spec_product/prod_graph_highlighted")
    #
    pdb.set_trace()

if __name__ == "__main__":
    # quad_test_async()
    quad_test_sync()
    pdb.set_trace()
