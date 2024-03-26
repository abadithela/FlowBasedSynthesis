import sys
sys.path.append('../..')
from components.maze_network import MazeNetwork, create_network_from_file
import networkx as nx
from ipdb import set_trace as st
import numpy as np


class FuelNetwork(MazeNetwork):
    def __init__(self, mazefile, obs = []):
        MazeNetwork.__init__(self, mazefile, obs = [])
        self.fuelcap = 10
        self.refuel = []
        self.setup_states()
        self.next_state_dict_w_fuel = None
        self.original_next_state_dict_w_fuel = None
        self.graph = self.create_graph_with_fuel_level()

    def setup_states(self):
        for z in range(0,self.len_z):
            for x in range(0,self.len_x):
                if self.map[(z,x)] != '*':
                    if self.map[(z,x)] == 'S':
                        self.init = (z,x)
                    if self.map[(z,x)] == 'T':
                        self.goal.append((z,x))
                    if self.map[(z,x)] == 'R':
                        self.refuel.append((z,x))
        # self.int = {pos: 'I' for pos in self.intermed}

    def dynamics_specs_w_fuel(self, x_str, z_str, f_str):
        dynamics_spec = set()
        for ii in range(0,self.len_z):
            for jj in range(0,self.len_x):
                for ff in range(0,self.fuelcap+1):
                    if not self.map[(ii,jj)] == '*':
                        if ((ii,jj),ff) in self.next_state_dict_w_fuel.keys():
                            next_steps_string = '('+z_str+' = '+str(ii)+' && '+x_str+' = '+str(jj)+' && '+f_str+'='+str(ff)+')'
                            # if (ii,jj) not in self.deadends:
                            for item in self.next_state_dict_w_fuel[((ii,jj),ff)]:
                                if (((ii,jj),ff), item) not in self.active_cuts:
                                    if item != ((ii,jj),ff):
                                        next_steps_string = next_steps_string + ' || ('+z_str+' = '+str(item[0][0])+' && '+x_str+' = '+str(item[0][1])+' && '+f_str+'='+str(item[-1])+')'
                            dynamics_spec |= {'('+z_str+' = '+str(ii)+' && '+x_str+' = '+str(jj)+' && '+f_str+'='+str(ff)+') -> X(('+ next_steps_string +'))'}
        # st()
        return dynamics_spec

    def augmented_dynamics_specs(self, x_str, z_str):
        dynamics_spec = set()
        for ii in range(0,self.len_z):
            for jj in range(0,self.len_x):
                if not self.map[(ii,jj)] == '*':
                    next_steps_string = '('+z_str+' = '+str(ii)+' && '+x_str+' = '+str(jj)+')'
                    if (ii,jj) not in self.deadends:
                        for item in self.next_state_dict[(ii,jj)]:
                            if item != (ii,jj):
                                next_steps_string = next_steps_string + ' || ('+z_str+' = '+str(item[0])+' && '+x_str+' = '+str(item[1])+')'
                        dynamics_spec |= {'('+z_str+' = '+str(ii)+' && '+x_str+' = '+str(jj)+') -> X(('+ next_steps_string +'))'}
        return dynamics_spec

    def create_graph_with_fuel_level(self):
        states = []
        for fuel_level in range(self.fuelcap+1):
            for x_s in range(self.len_x):
                for z_s in range(self.len_z):
                    if self.map[(z_s,x_s)] != '*':
                        if (z_s,x_s) not in self.refuel:
                            states.append(((z_s,x_s), fuel_level))
        for (z,x) in self.refuel:
            states.append(((z,x), self.fuelcap))

        transitions = []
        # adding system transitions
        next_state_dict = {}
        for state in states: #tester can move according to
            # for fuel_level in range(self.fuelcap):
            next_states = [(state)]
            fuel = state[-1]
            # if state not in self.deadends:
            if fuel > 0:
                # st()
                for next_state in self.next_state_dict[(state[0])]:
                    if next_state in self.refuel: # refuel
                        next_states.append(((next_state), self.fuelcap))
                    elif next_state != state[0]:
                        next_states.append(((next_state), fuel-1))

            next_state_dict.update({state: next_states})

        nodes = []
        nodes = states

        edges = []

        for state in states:
            # st()
            # if state not in self.goal: # when test done then done
            out_node = state
            in_nodes = [next_state for next_state in next_state_dict[state]]
            for in_node in in_nodes:
                actions = []
                if in_node in states:
                    actions.append((out_node, in_node))
                edges = edges + actions

        G = nx.DiGraph()
        G.add_nodes_from(nodes)
        G.add_edges_from(edges)

        to_remove = []
        for i, j in G.edges:
            if i == j:
                to_remove.append((i,j))
        G.remove_edges_from(to_remove)
        # st()

        self.next_state_dict_w_fuel = next_state_dict
        self.original_next_state_dict_w_fuel = next_state_dict
        
        return G

    def add_cut_w_fuel(self, cut):
        # st()
        self.next_state_dict_w_fuel[cut[0]].remove(cut[1])
        self.active_cuts.append(cut)

    def reset_maze(self):
        self.next_state_dict_w_fuel = self.original_next_state_dict_w_fuel
        st()
        self.active_cuts = []
