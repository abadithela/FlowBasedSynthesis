"""
Example automata
"""
import numpy as np
import spot
from itertools import chain, combinations
import pdb

def powerset(s):
    if type(s)==list:
        s = list(s)
    ps = list(chain.from_iterable(combinations(s, r) for r in range(len(s)+1)))
    return ps

class Automata:
    def __init__(self, Q, qinit, ap, delta, Acc):
        self.Q=Q
        self.qinit = qinit
        self.delta = delta
        self.ap = ap # Must be a list
        self.Sigma = powerset(ap)
        self.Acc = Acc
    
    def complement_negation(self, propositions):
        """
        Negation of all atomic propositions not listed in propositions
        """
        and_prop = spot.formula.And(list(propositions))
        comp_prop = [] # Complementary propositions
        for k in range(len(self.ap)):
            try:
                if not spot.contains(self.ap[k], and_prop):
                    comp_prop.append(spot.formula.Not(self.ap[k]))
            except:
                pdb.set_trace()
        # if propositions:
        #     pdb.set_trace()
        and_comp_prop = spot.formula.And(comp_prop)
        complete_formula = spot.formula.And([and_prop, and_comp_prop]) # Taking complement of complete formula
        return complete_formula

    def get_transition(self, q0, propositions):
        and_prop = spot.formula.And(list(propositions))
        transition = None
        for k,v in self.delta.items():
            if k[0] == q0:
                complete_formula = self.complement_negation(propositions)
                try:
                    if k[1] == True:
                        transition = v
                        return transition
                    if spot.contains(k[1], complete_formula):
                        transition = v
                        return transition
                except:
                    pdb.set_trace()
        return None

