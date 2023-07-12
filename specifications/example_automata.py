"""
File containing various automata examples:
"""
import spot 
from itertools import product

def get_neg(formula):
    return spot.formula.Not(formula)

def eventually(state_str="q", formula="goal"):
    nstates = 2
    AP = [spot.formula.ap(formula)]
    Q = [state_str+str(k) for k in range(nstates)]
    qinit = state_str+str(1)
    tau = {
            ("q1", AP[0]): "q0",
            ("q1", get_neg(AP[0])): "q1",
          }
    Acc = {"sys": ("q0",)}
    return Q, qinit, AP, tau, Acc

def async_eventually(state_str="q"):
    """
    Defining automaton for the simple eventually-eventually asynchronous product
    """
    nstates = 4
    AP = {"rf": spot.formula.ap("refuel"), "goal": spot.formula.ap("goal")}
    Q = [state_str+str(k) for k in range(nstates)]
    qinit = state_str+str(0)
    args_sys = eventually(state_str="qsys", formula="refuel")
    args_test = eventually(state_str="qtest", formula="goal")
    Qdict = dict()
    product_states = list(product(args_sys[0], args_test[0]))
    for k in range(len(Q)):
        Qdict[Q[k]] = product_states[k] 
    refuel = AP["rf"]
    goal = AP["goal"]
    tau = {
            ("q0", refuel): "q2",
            ("q0", goal): "q1",
            ("q0", get_neg(refuel)): "q0",
            ("q0", get_neg(goal)): "q0",

            ("q1", True): "q1",
            ("q1", refuel): "q3",
            ("q1", get_neg(refuel)): "q1",

            ("q2", goal): "q3",
            ("q2", True): "q2",
            ("q2", get_neg(goal)): "q2",

            ("q3", True): "q3",
          }
    Acc = {"sys": ("q1",), "test": ()} # accepting sets of states
    return Q, qinit, AP, tau, Acc, Qdict
