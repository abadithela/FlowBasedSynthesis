"""
Apurva Badithela, Josefine Graebener, 8/9/2023
Spot synchronous product automata for medium size grid example:

varphi_sys = <>(goal)
varphi_test = <>(int)

The function async_product constructs the asynchronous product of BAs of varphi_sys and varphi_test
and the function sync_product constructs the synchronous product of BAs of varphi_sys and varphi_test

Transcribed from visualize_automata.ipynb.
"""

import spot
from itertools import product

def neg(formula):
    return spot.formula.Not(formula)

def conjunction(formula_list):
    return spot.formula.And(formula_list)

def disjunction(formula_list):
    return spot.formula.Or(formula_list)

def get_b_sys(state_str="q"):
    """
    Asynchronous product automaton for the system specification
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


def sync_product(state_str="q"): # simplified
    """
    Asynchronous product automaton for the system and test specifications
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
