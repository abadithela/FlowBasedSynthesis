"""
Script to construct and test products
"""
import sys
import os
import pdb
from gridworld_specs import System
from product_automata_gridworld import async_eventually, sync_eventually
from automata import Automata
from products import Product

def construct_automata_async(AP_set=None):
    Q, qinit, AP, tau, Acc, Qdict = async_eventually(state_str="q")
    for ap in AP:
        assert ap in AP_set
    aut = Automata(Q, qinit, AP_set, tau, Acc)
    return aut

def construct_automata_sync(AP_set=None):
    Q, qinit, AP, tau, Acc, Qdict = sync_eventually(state_str="q")
    for ap in AP:
        assert ap in AP_set
    aut = Automata(Q, qinit, AP_set, tau, Acc)
    return aut

def construct_system():
    mazefile = "../simulations/mazefiles/maze.txt"
    system = System()
    system.construct_sys(mazefile)
    int_node_list = [(2,2)]
    system.add_intermediate_nodes(int_node_list)
    return system 

def sync_prod(system, aut):
    sys_prod = Product(system, aut)
    sys_prod.construct_labels()
    sys_prod.construct_transitions()
    return sys_prod  

def gridworld_sync():
    system = construct_system()
    aut = construct_automata_sync(AP_set = system.AP)
    prod_graph = sync_prod(system, aut)
    if not os.path.exists("imgs/sync_spec_product"):
        os.makedirs("imgs/sync_spec_product")
    system.save_plot("imgs/sync_spec_product/product_transys")
    aut.save_plot("imgs/sync_spec_product/specification_product")
    prod_graph.save_plot("imgs/sync_spec_product/prod_graph")
    pdb.set_trace()

def gridworld_async():
    system = construct_system()
    aut = construct_automata_async(AP_set = system.AP)
    prod_graph = sync_prod(system, aut)
    if not os.path.exists("imgs/async_spec_product"):
        os.makedirs("imgs/async_spec_product")
    system.save_plot("imgs/async_spec_product/product_transys")
    aut.save_plot("imgs/async_spec_product/specification_product")
    prod_graph.save_plot("imgs/async_spec_product/prod_graph")
    highlight_states={'red': [(((0, 0), (0, 1), 's'), 'q0'), (((0, 0), (1, 1), 's'), 'q0'), (((0, 0), (2, 1), 's'), 'q0')],
                      'magenta': [(((0, 0), (0, 1), 's'), 'q1'), (((0, 0), (1, 1), 's'), 'q1'), (((0, 0), (2, 1), 's'), 'q1')],
                      'cyan': [(((0, 0), (0, 1), 's'), 'q2'), (((0, 0), (1, 1), 's'), 'q2'), (((0, 0), (2, 1), 's'), 'q2')],
                      'green': [(((0, 0), (0, 1), 's'), 'q3'), (((0, 0), (1, 1), 's'), 'q3'), (((0, 0), (2, 1), 's'), 'q3')]
                      }
    prod_graph.highlight_states(highlight_states, "imgs/async_spec_product/prod_graph")
    pdb.set_trace()

if __name__ == "__main__":
    gridworld_async()
    pdb.set_trace()
    