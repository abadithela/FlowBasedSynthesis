from pdb import set_trace as st
import spot
import ast
import re

fn = "hoa_str_4_int.txt"
goal = spot.formula.ap("goal")
int_1 = spot.formula.ap("int_1")
int_2 = spot.formula.ap("int_2")
int_3 = spot.formula.ap("int_3")
int_4 = spot.formula.ap("int_4")
AP = [goal, int_1, int_2, int_3, int_4]
def neg(formula):
    return spot.formula.Not(formula)

def conjunction(formula_list):
    return spot.formula.And(formula_list)

def disjunction(formula_list):
    return spot.formula.Or(formula_list)

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

st()
