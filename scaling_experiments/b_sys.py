"""
Apurva Badithela, Josefine Graebener, 8/9/2023
Spot synchronous product automaton for the system specification:

varphi_sys = <>(goal)

Transcribed from visualize_automata.ipynb.
"""

import spot
from itertools import product
import sys
sys.path.append('..')
from components.tools import neg
from components.automaton import Automaton

def get_B_sys(AP_set):
    Q, qinit, AP, tau, Acc = B_sys(state_str="q")
    b_sys = Automaton(Q, qinit, AP_set, tau, Acc)
    return b_sys


def B_sys(state_str="q"):
    """
    Büchi automaton for the system specification.
    """
    nstates=2
    goal = spot.formula.ap("goal")
    AP = [goal]
    Q = [state_str+str(k) for k in range(nstates)]
    state_dict = {(1): "q0",
                 (0): "q1",
                 }
    qinit = state_str+str(0)

    tau = {
            ("q0", neg(goal)): "q0",
            ("q0", goal): "q1",

            ("q1", True): "q1",
            }
    Acc = {"sys": ("q1")} # accepting sets of states

    return Q, qinit, AP, tau, Acc
