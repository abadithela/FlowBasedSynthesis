"""
Apurva Badithela on 8/4/23
Spot synchronous and asynchronous product automata for parking test example:

varphi_sys = F(park & F(home))
varphi_test = G(park -> F(refuel))

The function async_product constructs the asynchronous product of BAs of varphi_sys and varphi_test
and the function sync_product constructs the synchronous product of BAs of varphi_sys and varphi_test
"""

import spot 
from itertools import product

def neg(formula):
    return spot.formula.Not(formula)

def conjunction(formula_list):
    return spot.formula.And(formula_list)

def disjunction(formula_list):
    return spot.formula.Or(formula_list)

def system_spec(state_str="q"):
    """
    System Buchi automaton for F(park & F home)
    """
    nstates=3
    home = spot.formula.ap("home")
    park = spot.formula.ap("park")
    AP = [home, park]
    Q = [state_str+str(k) for k in range(nstates)]
    qinit = state_str+str(0)
    tau = {
            ("q0", neg(park)): "q0",
            ("q0", conjunction([neg(home), park])): "q1",
            ("q0", conjunction([home, park])): "q3",

            ("q1", neg(home)): "q1",
            ("q1", home): "q3",

            ("q2", True): "q2",
          }

    Acc = ("q2") # accepting sets of states
    return Q, qinit, AP, tau, Acc

def tester_spec(state_str="q"):
    """
    System Buchi automaton for F(park & F home)
    """
    nstates=2
    park = spot.formula.ap("park")
    refuel = spot.formula.ap("refuel")
    AP = [refuel, park]
    Q = [state_str+str(k) for k in range(nstates)]
    qinit = state_str+str(0)
    tau = {
            ("q0", disjunction([neg(park), refuel])): "q0",
            ("q0", conjunction([neg(refuel), park])): "q1",

            ("q1", neg(refuel)): "q1",
            ("q1", refuel): "q0",
          }

    Acc = ("q0") # accepting sets of states
    return Q, qinit, AP, tau, Acc

def async_product(state_str="q"):
    """
    Asynchronous product automaton for the system and test specifications
    """
    nstates=6
    home = spot.formula.ap("home")
    park = spot.formula.ap("park")
    refuel = spot.formula.ap("refuel")
    AP = [home, park, refuel]
    Q = [state_str+str(k) for k in range(nstates)]
    qinit = state_str+str(0)
    tau = {
            ("q0", neg(park)): "q0",
            ("q0", disjunction([neg(park), refuel])): "q0",
            ("q0", conjunction([neg(refuel), park])): "q2",
            ("q0", conjunction([neg(home), park])): "q1",
            ("q0", conjunction([home, park])): "q3",

            ("q1", neg(home)): "q1",
            ("q1", disjunction([neg(park), refuel])): "q1",
            ("q1", home): "q3",
            ("q1", conjunction([park, neg(refuel)])): "q4",

            ("q2", neg(park)): "q2",
            ("q2", neg(refuel)): "q2",
            ("q2", refuel): "q0",
            ("q2", conjunction([park, neg(home)])): "q4",
            ("q2", conjunction([park, home])): "q5",

            ("q3", disjunction([neg(park), refuel])): "q3",
            ("q3", conjunction([park, neg(refuel)])): "q5",
            ("q3",True): "q3",

            ("q4", neg(refuel)): "q4",
            ("q4", neg(home)): "q4",
            ("q4", home): "q5",
            ("q4", refuel): "q1",
            
            ("q5", refuel): "q3",
            ("q5", neg(refuel)): "q5",
            ("q5", True): "q5",
          }
    Acc = {"sys": ("q3","q5"), "test": ("q0","q1","q3")} # accepting sets of states
    return Q, qinit, AP, tau, Acc
    
def player_labeled_async_product(state_str="q"):
    """
    Asynchronous product automaton for the system and test specifications
    """
    nstates=6
    home = spot.formula.ap("home")
    park = spot.formula.ap("park")
    refuel = spot.formula.ap("refuel")
    AP = [home, park, refuel]
    Q = [state_str+str(k) for k in range(nstates)]
    qinit = state_str+str(0)
    tau_sys = {
            ("q0", neg(park)): "q0",
            ("q0", conjunction([neg(home), park])): "q1",
            ("q0", conjunction([home, park])): "q3",

            ("q1", neg(home)): "q1",
            ("q1", home): "q3",

            ("q2", conjunction([park, neg(home)])): "q4",
            ("q2", conjunction([park, home])): "q5",

            ("q3",True): "q3",

            ("q4", neg(home)): "q4",
            ("q4", home): "q5",
            
            ("q5", True): "q5",
          }
    tau_test = {("q0", disjunction([neg(park), refuel])): "q0",
            ("q0", conjunction([neg(refuel), park])): "q2",

            ("q1", disjunction([neg(park), refuel])): "q1",
            ("q1", conjunction([park, neg(refuel)])): "q4",

            ("q2", neg(refuel)): "q2",
            ("q2", refuel): "q0",

            ("q3", disjunction([neg(park), refuel])): "q3",
            ("q3", conjunction([park, neg(refuel)])): "q5",

            ("q4", neg(refuel)): "q4",
            ("q4", refuel): "q1",
            
            ("q5", refuel): "q3",
            ("q5", neg(refuel)): "q5",
          }
    tau = {'s': tau_sys, 't': tau_test} 
            
    Acc = {"sys": ("q3","q5"), "test": ("q0","q1","q3")} # accepting sets of states
    return Q, qinit, AP, tau, Acc

def sync_product(state_str="q"):
    """
    Asynchronous product automaton for the system and test specifications
    """
    nstates=5
    home = spot.formula.ap("home")
    park = spot.formula.ap("park")
    refuel = spot.formula.ap("refuel")
    AP = [home, park, refuel]
    Q = [state_str+str(k) for k in range(nstates)]
    qinit = state_str+str(0)

    tau = {
            ("q0", neg(park)): "q0",
            ("q0", conjunction([neg(home), park, refuel])): "q1",
            ("q0", conjunction([neg(home), neg(refuel), park])): "q2",
            ("q0", conjunction([home, park, refuel])): "q3",
            ("q0", conjunction([neg(refuel), home, park])): "q4",

            ("q1", disjunction([conjunction([neg(home), refuel]), conjunction([neg(home), neg(park)])])): "q1",
            ("q1", conjunction([neg(home), park, neg(refuel)])): "q2",
            ("q1", disjunction([conjunction([home, refuel]), conjunction([home, neg(park)])])): "q3",
            ("q1", conjunction([home, park, neg(refuel)])): "q4",
            
            ("q2", conjunction([neg(refuel), park, neg(home)])): "q0",
            ("q2", conjunction([refuel, neg(home)])): "q1",
            ("q2", conjunction([neg(home),neg(refuel)])): "q2",
            ("q2", conjunction([refuel, home])): "q3",
            ("q2", conjunction([neg(refuel), home])): "q4",

            ("q3", disjunction([neg(park), refuel])): "q3",
            ("q3", conjunction([park, neg(refuel)])): "q4",

            ("q4", refuel): "q3",
            ("q4", neg(refuel)): "q4",        
          }
    Acc = {"sys": ("q3","q4"), "test": ("q0","q1","q3")} # accepting sets of states
    return Q, qinit, AP, tau, Acc
    