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
            ("q0", True): "q0",
          }
    Acc = {"sys": ("q0",)}
    return Q, qinit, AP, tau, Acc

def async_eventually(state_str="q"):
    """
    Defining automaton for the simple eventually-eventually asynchronous product
    """
    nstates = 4
    AP = [spot.formula.ap("sink"),  spot.formula.ap("int")]
    Q = [state_str+str(k) for k in range(nstates)]
    qinit = state_str+str(0)
    args_sys = eventually(state_str="qsys", formula="sink")
    args_test = eventually(state_str="qtest", formula="int")
    Qdict = dict()
    product_states = list(product(args_sys[0], args_test[0]))
    for k in range(len(Q)):
        Qdict[Q[k]] = product_states[k] 
    sink = AP[0]
    interm = AP[1]
    tau = {
            ("q0", sink): "q2",
            ("q0", interm): "q1",
            ("q0", get_neg(sink)): "q0",
            ("q0", get_neg(interm)): "q0",

            ("q1", True): "q1",
            ("q1", sink): "q3",
            ("q1", get_neg(sink)): "q1",

            ("q2", interm): "q3",
            ("q2", True): "q2",
            ("q2", get_neg(interm)): "q2",

            ("q3", True): "q3",
          }
    Acc = {"sys": ("q1","q3"), "test": ("q2","q3")} # accepting sets of states
    return Q, qinit, AP, tau, Acc, Qdict

def quadruped_maze(state_str="q"):
    """
    Defining automaton for the simple eventually-eventually asynchronous product
    """
    nstates = 6
    AP = [spot.formula.ap("sink"),  spot.formula.ap("int1"), spot.formula.ap("int2")]
    Q = [state_str+str(k) for k in range(nstates)]
    qinit = state_str+str(0)
    sink = AP[0]
    int1 = AP[1]
    int2 = AP[2]
    tau = {
            ("q0", get_neg(sink)): "q0",
            ("q0", sink): "q1",
            ("q0", spot.formula.And([int1, int2])): "q4",
            ("q0", spot.formula.And([int1, get_neg(int2)])): "q2",
            ("q0", get_neg(int1)): "q0",

            ("q1", True): "q1",
            ("q1", get_neg(int1)): "q1",
            ("q1", spot.formula.And([int1, int2])): "q5",
            ("q1", spot.formula.And([int1, get_neg(int2)])): "q3",
            
            ("q2", get_neg(sink)): "q2",
            ("q2", get_neg(int2)): "q2",
            ("q2", sink): "q3",
            ("q2", int2): "q4",

            ("q3", True): "q3",
            ("q3", get_neg(int2)): "q3",
            ("q3", int2): "q5",

            ("q4", True): "q4",
            ("q4", get_neg(sink)): "q4",
            ("q4", sink): "q5",

            ("q5", True): "q5",
          }
    Acc = {"sys": ("q1","q3","q5"), "test": ("q4","q5")} # accepting sets of states
    return Q, qinit, AP, tau, Acc