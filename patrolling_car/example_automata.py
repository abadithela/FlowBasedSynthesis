"""
File containing various automata examples:
"""
import spot 
from itertools import product

def neg(formula):
    return spot.formula.Not(formula)

def conjunction(formula_list):
    return spot.formula.And(formula_list)

def async_product(state_str="q"):
    """
    Asynchronous product automaton for the system and test specifications
    """
    nstates=6
    home = spot.formula.ap("home")
    park = spot.formula.ap("park")
    refuel = spot.formula.ap("refuel")
    empty = spot.formula.ap("empty")
    AP = [home, park, refuel, empty]
    Q = [state_str+str(k) for k in range(nstates)]
    qinit = state_str+str(0)
    
    sink = AP[0]
    interm = AP[1]
    tau = {
            ("q0", conjunction([neg(empty), home])): "q1",
            ("q0", refuel): "q2",
            ("q0", empty): "q3",
            ("q0", conjunction([neg(empty), neg(home)])): "q0",
            ("q0", neg(refuel)): "q0",

            ("q1", neg(empty)): "q1",
            ("q1", neg(refuel)): "q1",
            ("q1", empty): "q3",
            ("q1", refuel): "q4",

            ("q2", conjunction([neg(empty), home])): "q4",
            ("q2", True): "q2",
            ("q2", conjunction([neg(empty), neg(home)])): "q2",
            ("q2", empty): "q5",

            ("q3", True): "q3",
            ("q3", neg(refuel)): "q3",
            ("q3", refuel): "q5",

            ("q4", True): "q4",
            ("q4", neg(empty)): "q4",
            ("q4", empty): "q4",

            ("q5", True): "q5",
          }
    Acc = {"sys": ("q1","q4"), "test": ("q2","q4","q5")} # accepting sets of states
    return Q, qinit, AP, tau, Acc
    pass