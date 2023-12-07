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
from components.parse_specification_product import parse_spec_product
from components.automaton import Automaton
from ipdb import set_trace as st
import re


def get_B_product_automated():
    Q, qinit, AP, tau, Acc = construct_product(state_str="q")
    aut = Automaton(Q, qinit, AP, tau, Acc)
    return aut


def B_product(state_str="q"): # simplified
    """
    Synchronous product automaton for the system and test specifications
    """
    nstates=4
    goal = spot.formula.ap("goal")
    int = spot.formula.ap("gold")
    bank = spot.formula.ap("bank")

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

def construct_b_prod(state_str="q"):
    " Construct product directly from spot and parse"
    # System spec
    aut_sys = spot.translate('F(goal_1) & F(goal_2)', 'Buchi', 'state-based', 'complete')

    # Test spec
    aut_test = spot.translate('F(int)', 'Buchi', 'state-based', 'complete')

    # Specification product:
    spec_prod = spot.product(aut_sys, aut_test)

    # Convert to string:
    spec_prod_str = spec_prod.to_str('hoa')
    lines = spec_prod_str.split('\n')
    body_line = lines.index("--BODY--")
    end_line = lines.index("--END--")
    hoa = [lines[k] for k in range(len(lines)) if k > body_line and k < end_line]

    # Instantiating automata
    goal_1 = spot.formula.ap("goal_1")
    goal_2 = spot.formula.ap("goal_2")
    int = spot.formula.ap("int")
    formula_dict = {"t": True, "0": goal_1, "1": goal_2, "!0": neg(goal_1), "!1": neg(goal_2), "2": int, "!2": neg(int)}

    # st()
    AP = [goal_1, goal_2, int]
    nstates = 0
    for line in hoa:
        if 'State:' in line:
            nstates += 1
    Q = [state_str+str(k) for k in range(nstates)]
    qinit = state_str+str(0)
    tau = dict()
    Acc = dict()
    acc_states_sys = []
    acc_states_test = []
    for line in hoa:
        if 'State:' in line:
            out_state=line.split()[1]
            qout_st = "q" + out_state
            st()
            # how to keep track of the acceptance states for sys and tester
        else:
            # st()
            line_content = line.split()
            in_state = line_content[-1]
            propositions = line_content[:-1]
            qin_st = "q" + in_state
            spot_prop_list = []
            # find propositions between [ and ]
            # find propositions between [ and the first &
            # between & and &
            st()
            prop_list = re.split(r"[\[&\]]", propositions)
            prop_list = list(filter(None, prop_list))
            for prop_str in prop_list:
                spot_prop_list.append(formula_dict[prop_str])
            if len(spot_prop_list) > 1:
                formula = conjunction(spot_prop_list)
            else:
                formula = spot_prop_list[0]

            tau[(qout_st, formula)] = qin_st
    st()
    tau = parse_spec_product(spec_prod, formula_dict)
    st()
    Acc.update({"sys": acc_states_sys})
    Acc.update({"test": acc_states_test})
    return Q, qinit, AP, tau, Acc

if __name__ == '__main__':
    construct_b_prod()
