import re
import sys
sys.path.append('..')
from components.tools import neg, conjunction, disjunction
import spot
from collections import OrderedDict as od
from components.automaton import Automaton

def get_state_str(state):
    return "q"+str(state)

def read_state(state):
    '''
    Converting string state to an interger
    '''
    return int(state)

# Functions to take in spot formulas and return automaton object attributes:
def get_system_automaton(system_formula_str):
    spot_aut_sys = spot.translate(system_formula_str, 'Buchi', 'state-based', 'complete')
    Q_sys, qinit_sys, tau_sys, AP_sys = construct_automaton_attr(spot_aut_sys)
    Acc_sys = construct_Acc(spot_aut_sys, player="sys")

    aut_sys = Automaton(Q_sys, qinit_sys, AP_sys, tau_sys, Acc_sys)
    return aut_sys

def get_tester_automaton(tester_formula_str):
    spot_aut_test = spot.translate(tester_formula_str, 'Buchi', 'state-based', 'complete')
    Q_test, qinit_test, tau_test, AP_test = construct_automaton_attr(spot_aut_test)
    Acc_test = construct_Acc(spot_aut_test, player="test")

    aut_test = Automaton(Q_test, qinit_test, AP_test, tau_test, Acc_test)
    return aut_test

def get_prod_automaton(system_formula_str, tester_formula_str):
    spot_aut_sys = spot.translate(system_formula_str, 'Buchi', 'state-based', 'complete')
    spot_aut_test = spot.translate(tester_formula_str, 'Buchi', 'state-based', 'complete')
    spot_aut_prod = spot.product(spot_aut_sys, spot_aut_test)

    Q_prod, qinit_prod, tau_prod, AP_prod = construct_automaton_attr(spot_aut_prod)
    Acc_prod = construct_product_Acc(spot_aut_sys, spot_aut_test)

    aut_prod = Automaton(Q_prod, qinit_prod, AP_prod, tau_prod, Acc_prod)
    return aut_prod

def get_initial_state(spot_aut):
    spot_aut_str = spot_aut.to_str('hoa')
    lines = spot_aut_str.split('\n')
    for line in lines:
        if 'Start:' in line:
            init_state=read_state(line.split()[1])
            assert isinstance(init_state, int)
            break
    init_state = 'q' + str(init_state)
    return init_state

def get_formula_dict(spot_aut):
    '''
    Input: AP is a list of spot atomic propositions
    Get formula dict from a list of spot atomic propositions
    Formula dict is necessary for interpreting the atomic propositions
    '''
    AP = get_APs(spot_aut)
    formula_dict = {"t": True}
    num_AP = len(AP)
    for k in range(num_AP):
        formula_dict.update({str(k): AP[k]}) # Adding: {"k": AP[k]}
        formula_dict.update({"!"+str(k): neg(AP[k])}) # Adding: {"!k": neg(AP[k])}
    return formula_dict

def get_APs(spot_aut):
    '''
    Return a list of spot atomic propositions in a spot Buchi automaton
    '''
    spot_aut_str = spot_aut.to_str('hoa')
    lines = spot_aut_str.split('\n')
    AP = []
    for line in lines:
        if 'AP:' in line:
            parse_line = line.split()[1:]
            num_AP = int(parse_line[0])

            for k in range(1, len(parse_line)):
                ap_str = re.findall(r'"(.*?)"', parse_line[k])[0]
                assert isinstance(ap_str, str)

                # "Construct spot AP"
                ap = spot.formula.ap(ap_str)
                AP.append(ap)
            break
    return AP

def get_acc_states(spot_aut):
    '''
    Return a list of accepting states in the spot_automaton by parsing the body of the automaton
    In the prefix of the hoa_string, the succeeding portion of Acc refers to the number of accepting
    conditions in the automaton (double check)
    '''
    acc_states = []
    hoa_body = get_hoa_body(spot_aut)
    for line in hoa_body:
        if 'State:' in line:
            parse_line = line.split()
            state = parse_line[1]
            if len(parse_line) > 2:
                " If an acceptance condition is specified; might not be the best way"
                acc_states.append(read_state(state))
    assert acc_states != [] # Check that the algorithm worked.
    return acc_states

def construct_product_Acc(spot_aut_sys, spot_aut_test):
    '''
    Return the accepting state dictionary for the synchronous product of the system and tester acceptances
    '''
    Acc = dict()
    spec_prod = spot.product(spot_aut_sys, spot_aut_test)

    sys_prod_acc_states_str = []
    test_prod_acc_states_str = []

    # Individual accepting states
    sys_acc_states = get_acc_states(spot_aut_sys)
    test_acc_states = get_acc_states(spot_aut_test)

    # Product state dictionary and list:
    product_states, product_states_dict = get_product_states(spec_prod)

    # Matching the definition in the paper of how the acceptance conditions are tracked:
    for pair in product_states:
        if pair[0] in sys_acc_states:
            prod_st = product_states_dict[pair]
            prod_st_str = get_state_str(prod_st)
            sys_prod_acc_states_str.append(prod_st_str)

        if pair[1] in test_acc_states:
            prod_st = product_states_dict[pair]
            prod_st_str = get_state_str(prod_st)
            test_prod_acc_states_str.append(prod_st_str)

    assert sys_prod_acc_states_str != [] # Not empty sanity check
    Acc.update({"sys": sys_prod_acc_states_str})

    assert test_prod_acc_states_str != [] # Not empty sanity check
    Acc.update({"test": test_prod_acc_states_str})
    return Acc

def get_hoa_body(spot_aut):
    spot_aut_str = spot_aut.to_str('hoa')
    lines = spot_aut_str.split('\n')
    body_line = lines.index("--BODY--")
    end_line = lines.index("--END--")
    hoa_body = [lines[k] for k in range(len(lines)) if k > body_line and k < end_line]
    return hoa_body

def count_automaton_states(spot_aut):
    '''
    Input: Body of hoa string between the --BODY-- and --END-- lines
    Output: Number of states in the automaton
    '''
    hoa_body = get_hoa_body(spot_aut)
    nstates = 0
    for line in hoa_body:
        if 'State:' in line:
            nstates += 1
    return nstates

def get_product_states(spec_prod):
    '''
    Output:
    - product_states: list of pairs of states
    - product_states_dict: dictionary of product state pairs mapping to a state number
      as in: product_states_dict[pair_prod_state] = num_prod_state and
      product_states[num_prod_state] = pair_prod_state
    '''
    product_states = spec_prod.get_product_states()
    assert len(product_states) == count_automaton_states(spec_prod)
    product_states_dict = od()
    for k,prod in enumerate(product_states):
        product_states_dict.update({prod: k})
    return product_states, product_states_dict

def construct_automaton_attr(spot_aut):
    '''
    Function that returns attributes (except accepting conditions) needed to build an Automaton object from a spot automaton
    '''
    nstates = count_automaton_states(spot_aut)
    Q = [get_state_str(k) for k in range(nstates)]
    qinit = get_initial_state(spot_aut)
    tau = get_transitions(spot_aut)

    AP = get_APs(spot_aut)
    return Q, qinit, tau, AP

def construct_Acc(spot_aut, player="sys"):
    '''
    Constructing the Automaton attribute Acc for a single automaton
    '''
    Acc = dict()
    acc_states = get_acc_states(spot_aut)
    acc_states_str = [get_state_str(state) for state in acc_states]
    Acc.update({player: acc_states_str})
    return Acc

def parse_conjunction_str(conj_str, formula_dict):
    spot_prop_list = []
    prop_list = re.split(r"[\[&\]]", conj_str)
    prop_list = list(filter(None, prop_list))
    for prop_str in prop_list:
        spot_prop_list.append(formula_dict[prop_str])
    if len(spot_prop_list) > 1:
        formula = conjunction(spot_prop_list)
    else:
        formula = spot_prop_list[0]
    return formula

def parse_cnf_str(cnf_str, formula_dict):
    '''
    Unpacking a string cnf formula into a list of conjunctive formulas, and then parsing each of those
    conjunctive formulas separately
    '''
    conj_str_list = [x.strip() for x in re.split(r"\|", cnf_str)]

    # If no disjunctions, parse the conjunctive string into spot and return
    if len(conj_str_list) == 1:
        formula = parse_conjunction_str(conj_str_list[0], formula_dict)
    else:
        conj_formula_list = []
        for conj_str in conj_str_list:
            conj_formula = parse_conjunction_str(conj_str, formula_dict)
            conj_formula_list.append(conj_formula)
        formula = disjunction(conj_formula_list)
    return formula

def parse_hoa_transition_str(line):
    '''
    Function separating the hoa line into the cnf_portion, the incoming state, and
    any information on the accepting condition

    Input: Line with transition formula, input state, and transition acceptance as a string

    Output: CNF formula, input_state_str, and list of accepting conditions (if any).
    '''
    assert "[" in line
    assert "]" in line
    transition_acc_conditions = None # Default

    # CNF formula embedded within the first occurence of [ and the last occurence of ]
    cnf_str = line[line.find("[")+1: line.rfind("]")]

    # The rest of the string contains information on the incoming state, as well as any accepting
    # condition properties of that state.
    in_state_and_transition_acc = line[line.rfind("]")+1 :].split()
    in_state = read_state(in_state_and_transition_acc[0])
    qin_st = get_state_str(in_state)

    # See if there are any accepting conditions to catch:
    if len(in_state_and_transition_acc) > 1:
        transition_acc_conditions = in_state_and_transition_acc[1:]
    return cnf_str, qin_st, transition_acc_conditions


def get_transitions(spot_aut):
    formula_dict = get_formula_dict(spot_aut)
    hoa = get_hoa_body(spot_aut)
    tau = {}
    for line in hoa:
        if 'State:' in line:
            out_state=line.split()[1]
            qout_st = get_state_str(out_state)
        else:
            cnf_str, qin_st, transition_acc_conditions = parse_hoa_transition_str(line)
            formula = parse_cnf_str(cnf_str, formula_dict)
            tau[(qout_st, formula)] = qin_st
    return tau
