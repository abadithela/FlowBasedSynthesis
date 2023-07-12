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
                    comp_prop.append(self.ap[k])
            except:
                pdb.set_trace()
        and_comp_prop = spot.formula.And(comp_prop)
        complete_formula = spot.formula.And([and_prop, and_comp_prop]) # Taking complement of complete formula
        return complete_formula

    def get_transition(self, q0, propositions):
        and_prop = spot.formula.And(list(propositions))
        transition = None
        for k,v in self.delta.items():
            if k[0] == q0:
                complete_formula = self.complement_negation(propositions)
                if spot.contains(k[1], complete_formula):
                    transition = v
                    return transition
        return None

class AsyncProdAut(Automata):
    def __init__(self, Q, qinit, ap, delta, Acc, Qdict):
        super().__init__(Q, qinit, ap, delta, Acc)
        self.Qdict = Qdict

    def get_transition(self, q0, propositions):
        and_prop = spot.formula.And(list(propositions))
        transition = None
        for k,v in self.delta.items():
            if k[0] == q0:
                complete_formula = self.complement_negation(propositions)
                try:
                    if spot.contains(k[1], complete_formula):
                        transition = v
                        return transition
                except:
                    pdb.set_trace()
        assert transition is not None
        

# ap, cpl, cenv, col, neg_col, varphi = get_subformulas()
# Q = ["q0", "q1", "q2"]
# qinit = "q0"
# tau = {("q0", cpl[-1]): "q1", ("q0", spot.formula.And([col, spot.formula.Not(cpl[-1])])): "q2",
#        ("q0", spot.formula.And([neg_col, spot.formula.Not(cpl[-1])])): "q0", ("q1", True): "q1" , ("q2", True):"q2"}
# Acc = {("q1",)}
# Aut = Automata(Q, qinit, tau, Acc)

