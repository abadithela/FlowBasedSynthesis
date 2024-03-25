'''
Finding the graphs for the given problem data.
'''
import sys
sys.path.append('../..')
import os

from components.parse_specification_product import *
from components.transition_system import ProductTransys
from components.tools import synchronous_product
from components.setup_graphs import setup_nodes_and_edges
import time

def get_graphs(sys_formula, test_formula, mazefile, init, ints, goals, logger, obs=[], save_figures = True):
    runtimes = dict()

    t0 = time.time()
    b_sys = get_system_automaton(sys_formula)
    t_sys = time.time()
    runtimes["b_sys"] = t_sys - t0

    t_test_init = time.time()
    b_test = get_tester_automaton(test_formula)
    t_test_fin = time.time()
    runtimes["b_test"] = t_test_fin - t_test_init

    t_prod_init = time.time()
    b_pi = get_prod_automaton(sys_formula, test_formula)
    t_prod_fin = time.time()
    runtimes["b_prod"] = t_prod_fin - t_prod_init

    # get system
    system = ProductTransys()
    system.construct_sys(mazefile, init, ints, goals, obs)

    # get virtual sys
    t_sys_init = time.time()
    virtual_sys = synchronous_product(system, b_sys)
    t_sys_fin = time.time()
    runtimes["Gsys"] = t_sys_fin - t_sys_init

    # get virtual product
    t_graph_init = time.time()
    virtual = synchronous_product(system, b_pi)
    t_graph_fin = time.time()
    runtimes["G"] = t_graph_fin - t_graph_init

    # Saving data:
    save_data(logger, system, b_sys, b_test, b_pi, virtual, virtual_sys, runtimes)

    if save_figures:
        if not os.path.exists('imgs'):
            os.makedirs('imgs')
        b_test.save_plot('imgs/btest')
        b_sys.save_plot('imgs/bsys')
        b_pi.save_plot('imgs/bprod')
        virtual.plot_product_dot('imgs/virtual')
        virtual_sys.plot_product_dot('imgs/virtual_sys')

    return virtual, system, b_pi, virtual_sys

def save_data(logger, system, b_sys, b_test, b_pi, virtual, virtual_sys, runtimes):
    # Information about products:
    logger.save_data("Transition System", (len(system.S), len(system.E)))
    logger.save_data("Buchi (System)", (len(b_sys.Q), len(b_sys.delta)))
    logger.save_data("Buchi (Test)", (len(b_test.Q), len(b_test.delta)))
    logger.save_data("Buchi (Product)", (len(b_pi.Q), len(b_pi.delta)))
    logger.save_data("Gsys", (len(virtual_sys.S), len(virtual_sys.E)))
    logger.save_data("G", (len(virtual.S), len(virtual.E)))

    # Information about runtimes
    for k, runtime in runtimes.items():
        logger.save_runtime(k, runtime)
