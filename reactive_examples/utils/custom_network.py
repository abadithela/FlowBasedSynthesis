import sys
sys.path.append('..')
from ipdb import set_trace as st
import networkx as nx
from collections import OrderedDict as od
from problem_data import *

class CustomNetwork:
    def __init__(self, states, transitions, obs = []):
        self.init = None
        self.goal = []
        self.int = None
        self.obs = obs
        for obst in self.obs:
            self.map[(obst)] = '*'
        self.states = states
        self.transitions = transitions
        self.next_state_dict = None
        self.original_next_state_dict = None
        self.G = None
        self.active_cuts = []
        self.map , self.inv_map= self.make_state_map()
        self.setup_maze()
        # st()


    def set_int(self, int):
        self.int = int

    def set_goal(self,goal):
        self.goal = goal

    def setup_maze(self):
        self.next_state_dict = self.setup_next_states_map()
        self.G = self.create_graph()
        self.original_next_state_dict = self.next_state_dict

    def make_state_map(self):
        map = {}
        inv_map = {}
        for i,state in enumerate(self.states):
            map.update({i : state})
            inv_map.update({state : i})
        return map, inv_map

    def state_info(self, node):
        # returns system_state, tester_state, player
        return node[0], node[1], node[2]

    def print_maze(self):
        key_y_old = []
        printline = ""
        for key in self.map:
            key_y_new = key[0]
            if key_y_new == key_y_old:
                printline += self.map[key]
            else:
                print(printline)
                printline = self.map[key]
            key_y_old = key_y_new
        print(printline)
        printline = self.map[key]

    def create_graph(self):
        edges = []
        for state in self.states:
            if state not in self.goal: # collision states have no next state and when test done then done
                out_node = state
                in_nodes = [next_state for next_state in self.next_state_dict[state]]
                for in_node in in_nodes:
                    edges.append((out_node, in_node))

        G = nx.DiGraph()
        G.add_nodes_from(self.states)
        G.add_edges_from(edges)
        return G

    def setup_next_states_map(self):
        for state in self.states:
            if state in GOALS:
                self.goal.append(state)
            elif state in INIT:
                self.init = state

        next_state_dict = {}
        for state in self.states:
            next_states = [state]
            for transition in self.transitions:
                if transition[0] == state:
                    next_states.append(transition[1])
            next_state_dict.update({state: next_states})
        return next_state_dict


    def transition_specs(self, state_str):
        # st()
        dynamics_spec = set()
        for state_nr in self.map.keys():
            next_steps_string = '('+state_str+' = '+str(state_nr)+')'
            for item in self.next_state_dict[self.map[state_nr]][1:]:
                if not (self.map[state_nr],item) in self.active_cuts:
                    next_steps_string += '|| ('+state_str+' = '+str(self.inv_map[item])+')'
            dynamics_spec |= {'('+state_str+' = '+str(state_nr)+') -> X('+ next_steps_string +')'}
        return dynamics_spec

    def add_cut(self, cut):
        self.next_state_dict[cut[0]].remove(cut[1])
        self.active_cuts.append(cut)

    def reset_maze(self):
        self.next_state_dict = self.original_next_state_dict
        self.active_cuts = []
