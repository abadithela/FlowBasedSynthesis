'''
This script constructs automata from specifications using Spot. For constructing specifications, 
the specification can be entered as a string using:
f = spot.formula(f_str), or can be constructed from subformulas using the overloaded spot.formula method. 

See here for constructing formulae from strings: 

And, here for constructing formulae from subformulae:
        // atomic proposition
        formula::ap(string)
        // constants
        formula::ff();
        formula::tt();
        formula::eword();               // empty word (for regular expressions)
        // unary operators
        formula::Not(arg);
        formula::X(arg);
        formula::X(arg, min, max);     // X[min..max] arg
        formula::F(arg);
        formula::F(arg, min, max);     // F[min..max] arg
        formula::G(arg);
        formula::G(arg, min, max);     // G[min..max] arg
        formula::Closure(arg);
        formula::NegClosure(arg);
        formula::first_match(arg);      // SVA's first match operator
        // binary operators
        formula::Xor(left, right);
        formula::Implies(left, right);
        formula::Equiv(left, right);
        formula::U(left, right);        // (strong) until
        formula::R(left, right);        // (weak) release
        formula::W(left, right);        // weak until
        formula::M(left, right);        // strong release
        formula::EConcat(left, right);  // Seq
        formula::UConcat(left, right);  // Triggers
        // n-ary operators
        formula::Or({args,...});        // omega-rational Or
        formula::OrRat({args,...});     // rational Or (for regular expressions)
        formula::And({args,...});       // omega-rational And
        formula::AndRat({args,...});    // rational And (for regular expressions)
        formula::AndNLM({args,...});    // non-length-matching rational And (for r.e.)
        formula::Concat({args,...});    // concatenation (for regular expressions)
        formula::Fusion({args,...});    // concatenation (for regular expressions)
        // star-like operators
        formula::Star(arg, min, max);   // Star (for a Kleene star, set min=0 and omit max)
        formula::FStar(arg, min, max);  // Fusion Star
        // syntactic sugar built on top of previous operators
        formula::sugar_goto(arg, min, max); // arg[->min..max]
        formula::sugar_equal(arg, min, max); // arg[=min..max]
        formula::sugar_delay(left, right, min, max); // left ##[min..max] right
'''

import spot
import pdb
from IPython.display import display
import matplotlib.pyplot as plt
from itertools import chain, combinations

def powerset(s):
    if type(s)==list:
        s = list(s)
    ps = list(chain.from_iterable(combinations(s, r) for r in range(len(s)+1)))
    return ps

class Automata:
    def __init__(self, Q=None, qinit=None, delta=None, ap=None, Acc=None):
        self.Q=Q
        self.qinit = qinit
        self.delta = delta
        self.ap = set()
        self.pl_ap = dict()
        self.env_ap = dict()
        self.Sigma = set()
        self.Acc = Acc
        self.formula = None
    
    def set_pl_ap(self, *args):
        for ap_str in args:
            ap =  spot.formula.ap(ap_str)
            self.ap.add(ap)
            self.pl_ap[ap_str] = ap
    
    def set_env_ap(self, *args):
        for ap_str in args:
            ap =  spot.formula.ap(ap_str)
            self.ap.add(ap)
            self.env_ap[ap_str] = ap
    
    def set_alphabet(self):
        if not self.ap:
            self.ap = spot.atomic_prop_collect(self.formula)
        self.Sigma = powerset(ap)
        self.Acc = set() # T0-do
    
    def set_Acc(self, Acc):
        self.Acc = Acc

    def set_formula(self, f):
        if isinstance(f, 'str'):
            self.formula = spot.formula(f)
        else:
            self.formula = f
        
        self.set_alphabet()

    
    def get_transition(self, q0, true_aps, false_aps):
        '''
        Function check if a transition of the automaton is valid.
        true_aps: a list of atomic propositions that evaluate to true
        false_aps: a list of atomic propositions that evaluate to false.
        '''
        and_true_aps = spot.formula.And(true_aps)
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
        if not transition: # Condition is one not accepted by automaton.
            print("Condition not accepted by automaton")
            return None

def get_subformulas():
    subform = []
    ap = []
    cenv = []
    cpl = []
    for k in range(9):
        cenv_j = spot.formula.ap("cenv_"+str(k))
        cpl_j = spot.formula.ap("cpl_"+str(k))
        cenv.append(cenv_j)
        cpl.append(cpl_j)
        c = spot.formula.And([cenv_j, cpl_j])
        subform.append(c)
    ap.extend(cenv)
    ap.append(cpl)
    col = spot.formula.Or(subform)
    neg_col = spot.formula.Not(col)
    varphi = spot.formula.U(neg_col, cpl[-1])
    automata = spot.translate(varphi)
    return ap, cpl, cenv, col, neg_col, varphi

def example():
    ap, cpl, cenv, col, neg_col, varphi = get_subformulas()
    Q = ["q0", "q1", "q2"]
    qinit = "q0"
    tau = {("q0", cpl[-1]): "q1", ("q0", spot.formula.And([col, spot.formula.Not(cpl[-1])])): "q2",
        ("q0", spot.formula.And([neg_col, spot.formula.Not(cpl[-1])])): "q0", ("q1", True): "q1" , ("q2", True):"q2"}
    Acc = {("q1",)}
    Aut = Automata(Q=Q, qinit=qinit, delta=tau, ap=None, Acc=Acc)
    return Aut

if __name__ == "__main__":
    Aut = example()
    pdb.set_trace()

