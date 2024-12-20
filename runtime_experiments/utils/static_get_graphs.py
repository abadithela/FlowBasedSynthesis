'''
Finding the graphs for the given problem data.
'''
import sys
sys.path.append('../..')
import os
from ipdb import set_trace as st
import time
from components.parse_specification_product import *
from components.transition_system import ProductTransys
from components.tools import synchronous_product

def get_graphs_from_network(sys_formula, test_formula, network, init, ints, goals, instance_logger, logger_runtime_dict, obs=[], save_figures = False):
    runtimes = dict()

    t0 = time.time()
    b_sys = get_system_automaton(sys_formula)
    t_sys = time.time()
    runtimes["Buchi (Sys) RT"] = t_sys - t0

    t_test_init = time.time()
    b_test = get_tester_automaton(test_formula)
    t_test_fin = time.time()
    runtimes["Buchi (Test) RT"] = t_test_fin - t_test_init

    t_prod_init = time.time()
    b_pi = get_prod_automaton(sys_formula, test_formula)
    t_prod_fin = time.time()
    runtimes["Buchi (Product) RT"] = t_prod_fin - t_prod_init

    # get system
    # st()
    system = ProductTransys()

    system.construct_sys_from_network(network, init, ints, goals, obs)

    # st()
    # get virtual sys
    t_sys_init = time.time()
    virtual_sys = synchronous_product(system, b_sys)
    t_sys_fin = time.time()
    runtimes["Gsys RT"] = t_sys_fin - t_sys_init

    # get virtual product
    t_graph_init = time.time()
    virtual = synchronous_product(system, b_pi)
    t_graph_fin = time.time()
    runtimes["G RT"] = t_graph_fin - t_graph_init

    # Save data:
    save_data(instance_logger, system, b_sys, b_test, b_pi, virtual, virtual_sys, runtimes)
    logger_runtime_dict["graph_runtimes"].append(runtimes["G RT"])

    if save_figures:
        if not os.path.exists('imgs'):
            os.makedirs('imgs')
        b_test.save_plot('imgs/btest')
        b_sys.save_plot('imgs/bsys')
        b_pi.save_plot('imgs/bprod')
        virtual.plot_product_dot('imgs/virtual')
        virtual_sys.plot_product_dot('imgs/virtual_sys')

    return virtual, system, b_pi, virtual_sys

def get_graph_no_logger(sys_formula, test_formula, mazefile, init, ints, goals, obs=[], save_figures = False):
    b_sys = get_system_automaton(sys_formula)
    b_test = get_tester_automaton(test_formula)
    b_pi = get_prod_automaton(sys_formula, test_formula)
    system = ProductTransys()
    system.construct_sys(mazefile, init, ints, goals, obs)
    # get virtual sys
    virtual_sys = synchronous_product(system, b_sys)
    virtual = synchronous_product(system, b_pi)
    return virtual, system, b_pi, virtual_sys

def get_graphs(sys_formula, test_formula, mazefile, init, ints, goals, instance_logger, logger_runtime_dict, obs=[], save_figures = False):
    instance_logger.save_data("Init", init)
    instance_logger.save_data("Ints", ints)
    instance_logger.save_data("Goal", goals)

    runtimes = dict()

    t0 = time.time()
    b_sys = get_system_automaton(sys_formula)
    t_sys = time.time()
    runtimes["Buchi (Sys) RT"] = t_sys - t0

    t_test_init = time.time()
    b_test = get_tester_automaton(test_formula)
    t_test_fin = time.time()
    runtimes["Buchi (Test) RT"] = t_test_fin - t_test_init

    t_prod_init = time.time()
    b_pi = get_prod_automaton(sys_formula, test_formula)
    t_prod_fin = time.time()
    runtimes["Buchi (Product) RT"] = t_prod_fin - t_prod_init

    # get system
    system = ProductTransys()
    system.construct_sys(mazefile, init, ints, goals, obs)

    # get virtual sys
    t_sys_init = time.time()
    virtual_sys = synchronous_product(system, b_sys)
    t_sys_fin = time.time()
    runtimes["Gsys RT"] = t_sys_fin - t_sys_init

    # get virtual product
    t_graph_init = time.time()
    virtual = synchronous_product(system, b_pi)
    t_graph_fin = time.time()
    runtimes["G RT"] = t_graph_fin - t_graph_init

    # Saving data:
    save_data(instance_logger, system, b_sys, b_test, b_pi, virtual, virtual_sys, runtimes)
    logger_runtime_dict["graph_runtimes"].append(runtimes["G RT"])

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
    logger.save_data("Gsys", (len(virtual_sys.G_initial.nodes), len(virtual_sys.G_initial.edges)))
    logger.save_data("G", (len(virtual.G_initial.nodes), len(virtual.G_initial.edges)))

    # Information about runtimes
    for k, runtime in runtimes.items():
        logger.save_runtime(k, runtime)
