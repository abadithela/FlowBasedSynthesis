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
from pdb import set_trace as st

def get_B_product():
    Q, qinit, AP, tau, Acc = B_product(state_str="q")
    aut = Automaton(Q, qinit, AP, tau, Acc)
    return aut

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

def construct_product(state_str="q"):
    " Construct product directly from spot and parse"
    # System spec
    aut_sys = spot.translate('F(goal)', 'Buchi', 'state-based', 'complete')

    # Test spec
    aut_test = spot.translate('F(int)', 'Buchi', 'state-based', 'complete')

    # Specification product:
    spec_prod = spot.product(aut_sys, aut_test)

    # Convert to string:
    spec_prod_str = sync_prod.to_str('hoa')
    lines = spec_prod_str.split('\n')
    body_line = lines.index("--BODY--")
    end_line = lines.index("--END--")
    hoa = [lines[k] for k in range(len(lines)) if k > body_line and k < end_line]

    # Instantiating automata
    goal = spot.formula.ap("goal")
    int = spot.formula.ap("int")
    formula_dict = {"t": True, "0": goal, "1": int, "!0": neg(goal), "!1": neg(int)}
    
    AP = [goal, int]
    Q = [state_str+str(k) for k in range(nstates)]
    qinit = state_str+str(0)
    tau = dict()
    for line in hoa:
        if 'State:' in line:
            out_state=line.split()[1]
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
    st()
    tau = parse_spec_product(spec_prod, formula_dict)
    st()
    return Q, qinit, AP, tau, Acc
