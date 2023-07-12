"""
Example automata
"""
import numpy as np
import spot

class Automata:
    def __init__(self, Q, qinit, ap, delta, Acc):
        self.Q=Q
        self.qinit = qinit
        self.delta = delta
        self.ap = ap
        self.Sigma = powerset(ap)
        self.Acc = Acc
    
    def get_transition(self, q0, formula):
        conjunction = spot.formula.And(list(formula))
        transition = None
        for k,v in self.delta.items():
            if k[0] == q0:
                ctest = test(conjunction)
                try:
                    if spot.contains(k[1], ctest):
                        transition = v
                        return transition
                except:
                    pdb.set_trace()
        assert transition is not None

ap, cpl, cenv, col, neg_col, varphi = get_subformulas()
Q = ["q0", "q1", "q2"]
qinit = "q0"
tau = {("q0", cpl[-1]): "q1", ("q0", spot.formula.And([col, spot.formula.Not(cpl[-1])])): "q2",
       ("q0", spot.formula.And([neg_col, spot.formula.Not(cpl[-1])])): "q0", ("q1", True): "q1" , ("q2", True):"q2"}
Acc = {("q1",)}
Aut = Automata(Q, qinit, tau, Acc)

