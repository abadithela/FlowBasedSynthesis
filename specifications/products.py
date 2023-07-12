"""
File to construct asynchronous product and synchronous product.
"""
import sys
import spot
from spot.jupyter import display_inline
import buddy
import pdb
from collections import OrderedDict as od
from gridworld_specs import TranSys, System
from example_automata import *
from automata import Automata
import networkx as nx
from itertools import product, chain, combinations
spot.setup(show_default='.tvb')

def powerset(s):
    if type(s)==list:
        s = list(s)
    ps = list(chain.from_iterable(combinations(s, r) for r in range(len(s)+1)))
    return ps

class Product(TranSys):
    def __init__(self, system, automaton):
        super().__init__()
        self.system=system
        self.automaton=automaton
        self.S = list(product(system.S, automaton.Q))
        self.A = system.A
        self.I = (system.I, automaton.qinit)
        self.AP = automaton.Q
    
    def construct_transitions(self):
        self.E = dict()
        sys_state_pairs = list(product(self.system.S, self.system.S))
        aut_state_pairs = list(product(self.automaton.Q, self.automaton.Q))
        for s,t in sys_state_pairs:
            for a in self.system.A:
                if (s,a) in self.system.E.keys():
                    for q,p in aut_state_pairs:
                        valid_aut_transition = (self.system.E[(s,a)] == t)
                        label = self.system.L[t]
                        valid_sys_transition = (self.automaton.get_transition(q, label) == p)
                        if valid_sys_transition and valid_aut_transition:
                            self.E[((s,q), a)] = (t,p)

    def construct_labels(self):
        self.L = od()
        self.Sigma = powerset(self.AP)
        for s in self.S:
            self.L[s] = s[1]
    
    def identify_SIT(self):
        src_ap = spot.formula("src")
        int_ap = spot.formula("int")
        sink_ap = spot.formula("sink")
        self.src = [s for s in self.S if s[1] == self.automaton.qinit]
        try:
            self.int = [s for s in self.S if s[1] in self.automaton.Acc["test"]]
        except:
            self.int=[]
        self.sink = [s for s in self.S if s[1] in self.automaton.Acc["sys"]]

    def to_graph(self):
        self.G = nx.DiGraph()


def construct_automata(AP_set=None):
    Q, qinit, AP, tau, Acc = eventually(state_str="q", formula="sink")
    for ap in AP:
        assert ap in AP_set
    aut = Automata(Q, qinit, AP_set, tau, Acc)
    return aut

def construct_system():
    mazefile = "../gridworld/maze.txt"
    system = System()
    system.construct_sys(mazefile)
    return system

def sync_prod(system, aut):
    sys_prod = Product(system, aut)
    sys_prod.construct_labels()
    sys_prod.construct_transitions()
    return sys_prod

if __name__ == "__main__":
    system = construct_system()
    aut = construct_automata(AP_set = system.AP) # ensure that all system atomic propositions are maintained
    sys_prod = sync_prod(system, aut)
    pdb.set_trace()
    
