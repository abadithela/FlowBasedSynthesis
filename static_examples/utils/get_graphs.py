'''
Finding the graphs for the given problem data.
'''
import sys
sys.path.append('../..')
import os

from components.parse_specification_product import *
from components.transition_system import ProductTransys
from components.tools import synchronous_product

def get_graphs(sys_formula, test_formula, mazefile, init, ints, goals, obs=[], save_figures = True):
    b_sys = get_system_automaton(sys_formula)
    b_test = get_tester_automaton(test_formula)
    b_pi = get_prod_automaton(sys_formula, test_formula)

    # get system
    system = ProductTransys()
    system.construct_sys(mazefile, init, ints, goals, obs)

    # get virtual sys
    virtual_sys = synchronous_product(system, b_sys)
    # get virtual product
    virtual = synchronous_product(system, b_pi)

    if save_figures:
        if not os.path.exists('imgs'):
            os.makedirs('imgs')
        b_test.save_plot('imgs/btest')
        b_sys.save_plot('imgs/bsys')
        b_pi.save_plot('imgs/bprod')
        virtual.plot_product_dot('imgs/virtual')
        virtual_sys.plot_product_dot('imgs/virtual_sys')

    return virtual, system, b_pi, virtual_sys
