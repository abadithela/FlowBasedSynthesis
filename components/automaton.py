"""
Example automaton
"""
import numpy as np
import spot
from itertools import chain, combinations
import pdb
import networkx as nx

def powerset(s):
    if type(s)==list:
        s = list(s)
    ps = list(chain.from_iterable(combinations(s, r) for r in range(len(s)+1)))
    return ps

class Automaton:
    def __init__(self, Q, qinit, ap, delta, Acc):
        self.Q=Q
        self.qinit = qinit
        self.delta = delta
        self.ap = ap # Must be a list
        self.Sigma = powerset(ap)
        self.Acc = Acc

    def print_transitions(self):
        for k, v in self.delta.items():
            print("out state and formula: ", k, " in state: ", v)

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

    def plot_graph(self, fn):
        G_agr = nx.nx_agraph.to_agraph(self.G)
        # st()
        G_agr.node_attr['style'] = 'filled'
        G_agr.node_attr['gradientangle'] = 90

        for i in G_agr.nodes():
            n = G_agr.get_node(i)
            n.attr['shape'] = 'circle'
            n.attr['fillcolor'] = '#ffffff' # default color white
            # n.attr['label'] = ''
            try:
                if n in list(self.Acc["sys"]) and n not in list(self.Acc["test"]):
                    n.attr['fillcolor'] = '#ffb000' #yellow
            except:
                pass
            try:
                if n in list(self.Acc["sys"]):
                    n.attr['fillcolor'] = '#ffb000' #yellow
            except:
                pass

            try:
                if n in list(self.Acc["test"]) and n not in list(self.Acc["sys"]):
                    n.attr['fillcolor'] = '#648fff' # blue
            except:
                pass
            try:
                if n in list(self.Acc["test"]):
                    n.attr['fillcolor'] = '#648fff' # blue
            except:
                pass
            try:
                if n in list(self.Acc["test"]) and n in list(self.Acc["sys"]):
                    n.attr['fillcolor'] = '#ffb000' #yellow
            except:
                pass

        G_agr.draw(fn+"_aut.pdf",prog='dot')

    def to_graph(self):
        self.G = nx.DiGraph()
        self.G.add_nodes_from(self.Q)
        edges = []
        for state_act, in_node in self.delta.items():
            out_node = state_act[0]
            act = state_act[1]
            edge = (out_node, in_node)
            edges.append(edge)
        self.G.add_edges_from(edges)

    def save_plot(self, fn):
        self.to_graph()
        self.plot_graph(fn)
