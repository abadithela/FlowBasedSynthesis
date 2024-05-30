"""
Example automata
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

class Automata:
    def __init__(self, Q, qinit, ap, delta, Acc):
        self.Q=Q
        self.qinit = qinit
        self.delta = delta
        self.ap = ap # Must be a list
        self.Sigma = powerset(ap)
        self.Acc = Acc
    
    def is_player_labeled(self):
        if 's' in self.delta.keys() and 't' in self.delta.keys():
            return True
        else:
            return False

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

    def get_player_labeled_transition(self, q0, propositions, player):
        and_prop = spot.formula.And(list(propositions))
        transition = None
        player_delta = self.delta[player]
        for k,v in player_delta.items():
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
    
    def list_edges(self):
        pass

    def to_graph(self):
        self.G = nx.MultiGraph()
        self.G.add_nodes_from(list(self.Q))
        edges = []
        edge_attr = dict()
        node_attr = dict()
        # Will not work for player labeled states
        for state_prop, state_in in self.delta.items():
            # pdb.set_trace()
            state_out, prop = state_prop
            self.G.add_edge(state_out, state_in, label=str(prop))
    
    def save_plot(self, fn):
        """
        To Do. Either implement and save the graph from spot or convert to nx graph and save.
        second option preferred since it will then show if any mistakes have been made in transcribing 
        from Spot.
        """
        self.to_graph()
        G_agr = nx.nx_agraph.to_agraph(self.G)
        G_agr.node_attr['style'] = 'filled'
        # G_agr.node_attr['shape'] = 'circle'
        G_agr.node_attr['gradientangle'] = 90
        for i in G_agr.nodes():
            n = G_agr.get_node(i)
            if n in self.Acc["sys"] and n not in self.Acc["test"]:
                n.attr['fillcolor'] = 'yellow'
            elif n in self.Acc["test"] and n not in self.Acc["sys"]:
                n.attr['fillcolor'] = 'blue'          
            elif n in self.Acc["test"] and n in self.Acc["sys"]:
                n.attr['fillcolor'] = 'blue;0.5:yellow'
            else:
                n.attr['fillcolor'] = 'white'
        G_agr.draw(fn+"_dot.pdf",prog='dot')
 

