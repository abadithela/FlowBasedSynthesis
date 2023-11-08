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
import re

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
                 (0, 1): 7}
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


def sync_product(state_str="q"):
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

def sync_product_four_int(state_str="q"):
    """
    Asynchronous product automaton for the system and test specifications
    """
    nstates=32
    goal = spot.formula.ap("goal")
    int_1 = spot.formula.ap("int_1")
    int_2 = spot.formula.ap("int_2")
    int_3 = spot.formula.ap("int_3")
    int_4 = spot.formula.ap("int_4")
    AP = [goal, int_1, int_2, int_3, int_4]
    Q = [state_str+str(k) for k in range(nstates)]
    state_dict = {
        (1, 4): 0,
        (0, 4): 1,
        (1, 0): 2,
        (1, 1): 3,
        (1, 2): 4,
        (1, 3): 5,
        (1, 5): 6,
        (1, 6): 7,
        (1, 7): 8,
        (1, 8): 9,
        (1, 9): 10,
        (1, 10): 11,
        (1, 11): 12,
        (1, 12): 13,
        (1, 13): 14,
        (1, 14): 15,
        (1, 15): 16,
        (0, 15): 17,
        (0, 0): 18,
        (0, 1): 19,
        (0, 5): 20,
        (0, 14): 21,
        (0, 7): 22,
        (0, 13): 23,
        (0, 6): 24,
        (0, 12): 25,
        (0, 11): 26,
        (0, 10): 27,
        (0, 9): 28,
        (0, 8): 29,
        (0, 2): 30,
        (0, 3): 31}
    qinit = state_str+str(0)
    fn = "hoa_str_4_int.txt"
    formula_dict = {"t": True, "0": goal, "1": int_1, "2": int_2, "3":int_3, "4":int_4, "!0": neg(goal), "!1": neg(int_1), "!2": neg(int_2), "!3":neg(int_3), "!4":neg(int_4)}

    tau = dict()
    with open(fn) as file:
        for line in file:
            if 'State:' in line:
                out_state=line.split()[-1]
                qout_st = "q" + out_state
            else:
                propositions, in_state = line.split()
                qin_st = "q" + in_state
                spot_prop_list = []
                # find propositions between [ and ]
                # find propositions between [ and the first &
                # between & and & 
                prop_list = re.split(r"[\[&\]]", propositions)
                prop_list = list(filter(None, prop_list))
                for prop_str in prop_list:
                    spot_prop_list.append(formula_dict[prop_str])
                if len(spot_prop_list) > 1:
                    formula = conjunction(spot_prop_list)
                else:
                    formula = spot_prop_list[0]
                tau[(qout_st, formula)] = qin_st
        sys_acc = ["q1"] + ["q"+str(i) for i in range(17,32)]
        Acc = {"sys": tuple(sys_acc), "test": ("q2","q18")} # accepting sets of states
    return Q, qinit, AP, tau, Acc

