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


def B_product(state_str="q"):
    """
    Asynchronous product automaton for the system and test specifications
    """
    nstates=8
    goal = spot.formula.ap("goal")
    int_1 = spot.formula.ap("int_1")
    int_2 = spot.formula.ap("int_2")
    AP = [goal, int_1, int_2]
    Q = [state_str+str(k) for k in range(nstates)]
    state_dict = {(1, 2): 0,
                 (0, 2): 1,
                 (1, 0): 2,
                 (1, 1): 3,
                 (1, 3): 4,
                 (0, 3): 5,
                 (0, 0): 6,
                 (0, 1): 7,
                 }
    qinit = state_str+str(0)

    tau = {
            ("q0", conjunction([neg(goal), conjunction([neg(int_1), neg(int_2)])])): "q0",
            ("q0", conjunction([goal, conjunction([neg(int_1), neg(int_2)])])): "q1",
            ("q0", conjunction([goal, conjunction([int_1, neg(int_2)])])): "q7",
            ("q0", conjunction([neg(goal), conjunction([int_1, neg(int_2)])])): "q3",
            ("q0", conjunction([goal, conjunction([neg(int_1), int_2])])): "q5",
            ("q0", conjunction([neg(goal), conjunction([neg(int_1), int_2])])): "q4",
            ("q0", conjunction([neg(goal), conjunction([int_1, int_2])])): "q2",

            ("q1", conjunction([neg(int_1), neg(int_2)])): "q1",
            ("q1", conjunction([int_1, int_2])): "q6",
            ("q1", conjunction([int_1, neg(int_2)])): "q7",
            ("q1", conjunction([neg(int_1), int_2])): "q5",

            ("q2", neg(goal)): "q2",
            ("q2", goal): "q6",

            ("q3", conjunction([neg(goal), neg(int_2)])): "q3",
            ("q3", conjunction([goal, neg(int_2)])): "q7",
            ("q3", conjunction([goal, int_2])): "q6",
            ("q3", conjunction([neg(goal), int_2])): "q2",

            ("q4", conjunction([neg(goal), neg(int_1)])): "q4",
            ("q4", conjunction([goal, neg(int_1)])): "q5",
            ("q4", conjunction([neg(goal), int_1])): "q2",
            ("q4", conjunction([goal, int_1])): "q6",

            ("q5", neg(int_1)): "q5",
            ("q5", int_1): "q6",

            ("q6", True): "q6",

            ("q7", neg(int_2)): "q7",
            ("q7", int_2): "q6",
          }
    Acc = {"sys": ("q1","q5", "q6", "q7"), "test": ("q2","q6")} # accepting sets of states
    return Q, qinit, AP, tau, Acc
