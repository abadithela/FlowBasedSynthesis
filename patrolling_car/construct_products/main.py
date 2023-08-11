"""
Script to construct and test products
"""
import sys
import os
# sys.path.append("/Users/apurvabadithela/software/VisualizeAutomata/patrolling_car")
import pdb
from product_transys import ProductTransys, Transys
import automata.example_automata as example_automata
import automata.parking_test as parking_test 
from automata.automata import Automata
import plotting
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

def construct_sync_aut_parking_test(AP_set = None):
    Q, qinit, AP, tau, Acc = parking_test.sync_product(state_str="q")
    for ap in AP:
        assert ap in AP_set
    aut = Automata(Q, qinit, AP_set, tau, Acc)
    return aut

def construct_async_aut_parking_test(AP_set = None):
    Q, qinit, AP, tau, Acc = parking_test.async_product(state_str="q")
    for ap in AP:
        assert ap in AP_set
    aut = Automata(Q, qinit, AP_set, tau, Acc)
    return aut

def construct_async_player_labeled_aut_parking_test(AP_set=None):
    Q, qinit, AP, tau, Acc = parking_test.player_labeled_async_product(state_str="q")
    for ap in AP:
        assert ap in AP_set
    aut = Automata(Q, qinit, AP_set, tau, Acc)
    return aut

def sync_prod_player_labeled(system, aut):
    sys_prod = Product(system, aut)
    sys_prod.construct_labels()
    sys_prod.construct_transitions_player_labeled()
    return sys_prod

def construct_system_parking_test():
    """
    Construct system from maze.txt
    """
    mazefile = "../graph/mazefiles/small_maze.txt"
    system = ProductTransys()
    system.construct_sys(mazefile)
    return system  

def parking_test_async():
    system = construct_system_parking_test()
    aut = construct_async_aut_parking_test(AP_set = system.AP)
    prod_graph = sync_prod(system, aut)
    if not os.path.exists("imgs/parking_test/async_spec_product"):
        os.makedirs("imgs/parking_test/async_spec_product")
    system.save_plot("imgs/parking_test/async_spec_product/product_transys")
    # aut.save_plot("imgs/parking_test/async_spec_product/specification_product")
    prod_graph.save_plot("imgs/parking_test/async_spec_product/prod_graph")
    highlight_states={'red': [(((0, 0), (0, 1), 's'), 'q0'), (((0, 0), (1, 1), 's'), 'q0'), (((0, 0), (2, 1), 's'), 'q0')],
                      'magenta': [(((0, 0), (0, 1), 's'), 'q1'), (((0, 0), (1, 1), 's'), 'q1'), (((0, 0), (2, 1), 's'), 'q1')],
                      'cyan': [(((0, 0), (0, 1), 's'), 'q2'), (((0, 0), (1, 1), 's'), 'q2'), (((0, 0), (2, 1), 's'), 'q2')],
                      'green': [(((0, 0), (0, 1), 's'), 'q3'), (((0, 0), (1, 1), 's'), 'q3'), (((0, 0), (2, 1), 's'), 'q3')]
                      }
    prod_graph.highlight_states(highlight_states, "imgs/parking_test/async_spec_product/prod_graph")
    pdb.set_trace()

def parking_test_sync():
    system = construct_system_parking_test()
    aut = construct_sync_aut_parking_test(AP_set = system.AP)
    prod_graph = sync_prod(system, aut)
    if not os.path.exists("imgs/parking_test/sync_spec_product"):
        os.makedirs("imgs/parking_test/sync_spec_product")
    system.save_plot("imgs/parking_test/sync_spec_product/product_transys")
    # aut.save_plot("imgs/parking_test/sync_spec_product/specification_product")
    prod_graph.save_plot("imgs/parking_test/sync_spec_product/prod_graph")
    pdb.set_trace()

def parking_test_async_player_labeled():
    system = construct_system_parking_test()
    aut = construct_async_player_labeled_aut_parking_test(AP_set = system.AP)
    prod_graph = sync_prod_player_labeled(system, aut)
    if not os.path.exists("imgs/parking_test/async_spec_product_player_labeled"):
        os.makedirs("imgs/parking_test/async_spec_product_player_labeled")
    system.save_plot("imgs/parking_test/async_spec_product_player_labeled/product_transys")
    # aut.save_plot("imgs/parking_test/sync_spec_product/specification_product")
    prod_graph.save_plot("imgs/parking_test/async_spec_product_player_labeled/prod_graph")
    pdb.set_trace()

if __name__ == "__main__":
    parking_test_async_player_labeled()
    pdb.set_trace()
    