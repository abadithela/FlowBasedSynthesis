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
from components.tools import neg, conjunction
from components.automaton import Automaton
from components.parse_specification_product import parse_spec_product

from ipdb import set_trace as st
import re


def get_B_sys_automated():
    Q, qinit, AP, tau, Acc = construct_b_sys(state_str="q")
    aut = Automaton(Q, qinit, AP, tau, Acc)
    return aut


def construct_b_sys(state_str="q"):
    " Construct product directly from spot and parse"
    # System spec
    aut_sys = spot.translate('F(goal_1) & F(goal_2)', 'Buchi', 'state-based', 'complete')

    # Convert to string:
    spec_prod_str = aut_sys.to_str('hoa')
    lines = spec_prod_str.split('\n')
    body_line = lines.index("--BODY--")
    end_line = lines.index("--END--")
    hoa = [lines[k] for k in range(len(lines)) if k > body_line and k < end_line]

    # Instantiating automata
    goal_1 = spot.formula.ap("goal_1")
    goal_2 = spot.formula.ap("goal_2")

    formula_dict = {"t": True, "0": goal_1, "1": goal_2, "!0": neg(goal_1), "!1": neg(goal_2)}

    AP = [goal_1, goal_2]
    nstates = 0
    for line in hoa:
        if 'State:' in line:
            nstates += 1

    Q = [state_str+str(k) for k in range(nstates)]
    qinit = state_str+str(0)
    tau = dict()
    Acc = dict()
    acc_states = []
    for line in hoa:
        if 'State:' in line:
            out_state=line.split()[1]
            qout_st = "q" + out_state
            if line.split()[-1] == '{0}': # defining the system acceptance states
                acc_states.append(qout_st)
        else:
            line_content = line.split()
            in_state = line_content[-1]
            propositions = line_content[:-1][0]
            qin_st = "q" + in_state
            spot_prop_list = []
            # find propositions between [ and ]
            # find propositions between [ and the first &
            # between & and &
            # st()
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
    tau = parse_spec_product(aut_sys, formula_dict)
    st()
    Acc.update({"sys": acc_states})
    return Q, qinit, AP, tau, Acc

if __name__ == '__main__':
    construct_b_sys()
