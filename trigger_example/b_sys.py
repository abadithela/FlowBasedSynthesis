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
import re

def get_B_sys(AP_set):
    Q, qinit, AP, tau, Acc = B_sys(state_str="q")
    b_sys = Automaton(Q, qinit, AP_set, tau, Acc)
    return b_sys

def get_B_sys_automated():
    Q, qinit, AP, tau, Acc = construct_product(state_str="q")
    aut = Automaton(Q, qinit, AP, tau, Acc)
    return aut


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

def construct_product(state_str="q"):
    " Construct product directly from spot and parse"
    # System spec
    aut_sys = spot.translate('F(goal) & [](gold -> <>(bank))', 'Buchi', 'state-based', 'complete')

    # Convert to string:
    spec_prod_str = aut_sys.to_str('hoa')
    lines = spec_prod_str.split('\n')
    body_line = lines.index("--BODY--")
    end_line = lines.index("--END--")
    hoa = [lines[k] for k in range(len(lines)) if k > body_line and k < end_line]

    # Instantiating automata
    goal = spot.formula.ap("goal")
    gold = spot.formula.ap("gold")
    bank = spot.formula.ap("bank")


    formula_dict = {"t": True, "0": goal, "1": gold, "!0": neg(goal), "!1": neg(gold), "2": bank, "!2": neg(bank)}
    from ipdb import set_trace as st
    st()
    AP = [goal, gold, bank]
    nstates = 0
    for line in hoa:
        if 'State:' in line:
            nstates += 1

    Q = [state_str+str(k) for k in range(nstates)]
    qinit = state_str+str(0)
    tau = dict()
    for line in hoa:
        if 'State:' in line:
            out_state=line.split()[1]
            qout_st = "q" + out_state
        else:
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
    return Q, qinit, AP, tau, Acc
