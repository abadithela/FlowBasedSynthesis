"""
Apurva Badithela, Josefine Graebener, 8/9/2023
Spot synchronous and asynchronous product automata for quadruped track example:

varphi_sys = <>(goal)
varphi_test = <>(int_1) & <>(int_2)

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

def async_product(state_str="q"):
    """
    Asynchronous product automaton for the system and test specifications
    """
    nstates=16
    goal = spot.formula.ap("goal")
    int_1 = spot.formula.ap("int_1")
    int_2 = spot.formula.ap("int_2")
    int_3 = spot.formula.ap("int_3")
    AP = [goal, int_1, int_2, int_3]
    Q = [state_str+str(k) for k in range(nstates)]
    state_dict = {(1, 3): 0,
                (0, 0): 1,
                (0, 1): 2,
                (0, 2): 3,
                (0, 3): 4,
                (0, 4): 5,
                (0, 5): 6,
                (0, 6): 7,
                (0, 7): 8,
                (1, 0): 9,
                (1, 1): 10,
                (1, 2): 11,
                (1, 4): 12,
                (1, 5): 13,
                (1, 6): 14,
                (1, 7): 15}
    qinit = state_str+str(0)
    tau = {
            ("q0", neg(goal)): "q0",
            ("q0", conjunction([neg(int_1), neg(int_2)])): "q0",
            ("q0", goal): "q1",
            ("q0", conjunction([neg(int_1), int_2])): "q4",
            ("q0", conjunction([int_1, neg(int_2)])): "q3",
            ("q0", conjunction([int_1, int_2])) : "q2",

            ("q1", conjunction([neg(int_1), neg(int_2)])): "q1",
            ("q1", conjunction([int_1, int_2])): "q6",
            ("q1", conjunction([neg(int_1), int_2])): "q5",
            ("q1", conjunction([int_1, neg(int_2)])): "q7",
            ("q1", True): "q1",

            ("q2", neg(goal)): "q2",
            ("q2", goal): "q6",
            ("q2", True): "q2",

            ("q3", neg(goal)): "q3",
            ("q3", neg(int_2)): "q3",
            ("q3", int_2): "q2",
            ("q3", goal): "q7",

            ("q4", neg(goal)): "q4",
            ("q4", neg(int_1)): "q4",
            ("q4", goal): "q5",
            ("q4", int_1): "q2",

            ("q5", neg(int_1)): "q5",
            ("q5", int_1): "q6",
            ("q5", True): "q5",

            ("q6", True): "q6",

            ("q7", neg(int_2)): "q7",
            ("q7", int_2): "q6",
            ("q7", True): "q7"
          }

    Acc = {"sys": ("q1","q5", "q6", "q7"), "test": ("q2","q6")} # accepting sets of states
    return Q, qinit, AP, tau, Acc


def get_b_sys(state_str="q"):
    """
    Asynchronous product automaton for the system and test specifications
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
    nstates=16
    goal = spot.formula.ap("goal")
    int_1 = spot.formula.ap("int_1")
    int_2 = spot.formula.ap("int_2")
    int_3 = spot.formula.ap("int_3")
    AP = [goal, int_1, int_2, int_3]
    Q = [state_str+str(k) for k in range(nstates)]
    state_dict = {(1, 3): 0,
                (0, 0): 1,
                (0, 1): 2,
                (0, 2): 3,
                (0, 3): 4,
                (0, 4): 5,
                (0, 5): 6,
                (0, 6): 7,
                (0, 7): 8,
                (1, 0): 9,
                (1, 1): 10,
                (1, 2): 11,
                (1, 4): 12,
                (1, 5): 13,
                (1, 6): 14,
                (1, 7): 15}
    qinit = state_str+str(0)

    tau = {
            ("q0", conjunction([goal, neg(int_1), neg(int_2), neg(int_3)])): "q4",
            ("q0", conjunction([neg(goal), int_1, neg(int_2), neg(int_3)])): "q11",
            ("q0", conjunction([neg(goal), neg(int_1), neg(int_2), neg(int_3)])): "q0",
            ("q0", conjunction([neg(goal), neg(int_1), int_2, neg(int_3)])): "q14",
            ("q0", conjunction([neg(goal), neg(int_1), neg(int_2), int_3])): "q15",

            ("q1", True): "q1",

            ("q2", conjunction([neg(int_3)])): "q2",
            ("q2", conjunction([int_3])): "q1",

            ("q3", conjunction([neg(int_2), neg(int_3)])): "q3",
            ("q3", conjunction([int_2, neg(int_3)])): "q2",
            ("q3", conjunction([neg(int_2), int_3])): "q6",

            ("q4", conjunction([neg(int_1), neg(int_2), neg(int_3)])): "q4",
            ("q4", conjunction([int_1, neg(int_2), neg(int_3)])): "q3",
            ("q4", conjunction([neg(int_1), int_2, neg(int_3)])): "q7",
            ("q4", conjunction([neg(int_1), neg(int_2), int_3])): "q8",

            ("q5", conjunction([neg(int_1)])): "q5",
            ("q5", conjunction([int_1])): "q1",

            ("q6", conjunction([neg(int_2)])): "q6",
            ("q6", conjunction([int_2])): "q1",

            ("q7", conjunction([neg(int_1), neg(int_3)])): "q7",
            ("q7", conjunction([int_1, neg(int_3)])): "q2",
            ("q7", conjunction([neg(int_1), int_3])): "q5",

            ("q8", conjunction([neg(int_1), neg(int_2)])): "q8",
            ("q8", conjunction([int_1, neg(int_2)])): "q6",
            ("q8", conjunction([neg(int_1), int_2])): "q5",

            ("q9", conjunction([neg(goal)])): "q9",
            ("q9", conjunction([goal])): "q1",

            ("q10", conjunction([neg(goal), neg(int_3)])): "q10",
            ("q10", conjunction([goal, neg(int_3)])): "q2",
            ("q10", conjunction([neg(goal), int_3])): "q9",

            ("q11", conjunction([neg(goal), neg(int_2), neg(int_3)])): "q11",
            ("q11", conjunction([goal, neg(int_2), neg(int_3)])): "q3",
            ("q11", conjunction([neg(goal), int_2, neg(int_3)])): "q10",
            ("q11", conjunction([neg(goal), neg(int_2), int_3])): "q13",

            ("q12", conjunction([neg(goal), neg(int_1)])): "q12",
            ("q12", conjunction([goal, neg(int_1)])): "q5",
            ("q12", conjunction([neg(goal), int_1])): "q9",

            ("q13", conjunction([neg(goal), neg(int_2)])): "q13",
            ("q13", conjunction([goal, neg(int_2)])): "q6",
            ("q13", conjunction([neg(goal), int_2])): "q9",

            ("q14", conjunction([neg(goal), neg(int_1), neg(int_3)])): "q14",
            ("q14", conjunction([goal, neg(int_1), neg(int_3)])): "q7",
            ("q14", conjunction([neg(goal), int_1, neg(int_3)])): "q10",
            ("q14", conjunction([neg(goal), neg(int_1), int_3])): "q12",

            ("q15", conjunction([neg(goal), neg(int_1), neg(int_2)])): "q15",
            ("q15", conjunction([goal, neg(int_1), neg(int_2)])): "q8",
            ("q15", conjunction([neg(goal), neg(int_1), int_2])): "q12",
            ("q15", conjunction([neg(goal), int_1, neg(int_2)])): "q13"

          }
    Acc = {"sys": ("q1","q2", "q3", "q4", "q5", "q6", "q7", "q8"), "test": ("q1","q9")} # accepting sets of states
    return Q, qinit, AP, tau, Acc
