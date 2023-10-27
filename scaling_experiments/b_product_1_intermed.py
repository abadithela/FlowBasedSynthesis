"""
Apurva Badithela, Josefine Graebener, 8/9/2023
Spot synchronous product automaton for the system and test specifications:

varphi_sys = <>(goal)
varphi_test = <>(int)

The function get_B_product constructs the synchronous product of BAs of varphi_sys and varphi_test.

Transcribed from visualize_automata.ipynb.
"""

import spot
from itertools import product
import sys
sys.path.append('..')
from components.tools import neg, conjunction
from components.automaton import Automaton

def get_B_product():
    Q, qinit, AP, tau, Acc = B_product(state_str="q")
    aut = Automaton(Q, qinit, AP, tau, Acc)
    return aut

def B_product(state_str="q"): # simplified
    """
    Synchronous product automaton for the system and test specifications
    """
    nstates=4
    goal = spot.formula.ap("goal")
    int = spot.formula.ap("int")

    AP = [goal, int]
    Q = [state_str+str(k) for k in range(nstates)]
    state_dict = {(1, 1): 0,
                (0, 0): 1,
                (0, 1): 2,
                (1, 0): 3}
    qinit = state_str+str(0)

    tau = {
            ("q0", conjunction([neg(goal), neg(int)])): "q0",
            ("q0", conjunction([goal, neg(int)])): "q2",
            ("q0", conjunction([neg(goal), int])): "q3",
            ("q0", conjunction([goal, int])): "q1",

            ("q1", True): "q1",

            ("q2", neg(int)): "q2",
            ("q2", int): "q1",

            ("q3", neg(goal)): "q3",
            ("q3", goal): "q1",

          }
    Acc = {"sys": ("q1","q2"), "test": ("q1","q3")} # accepting sets of states

    return Q, qinit, AP, tau, Acc
