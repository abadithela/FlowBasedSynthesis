import re
import sys
sys.path.append('..')
from components.tools import neg, conjunction
import spot

def get_hoa_list(spec_prod):
    spec_prod_str = spec_prod.to_str('hoa')
    lines = spec_prod_str.split('\n')
    body_line = lines.index("--BODY--")
    end_line = lines.index("--END--")
    hoa = [lines[k] for k in range(len(lines)) if k > body_line and k < end_line]
    return hoa

def parse_spec_product(spec_prod, formula_dict):
    hoa = get_hoa_list(spec_prod)
    tau = {}
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
    return tau
