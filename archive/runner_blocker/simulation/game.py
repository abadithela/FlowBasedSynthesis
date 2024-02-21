from ipdb import set_trace as st
from copy import deepcopy
# from find_cuts import find_cuts
import random

class Game:
    def __init__(self, maze, sys, tester):
        self.maze = deepcopy(maze)
        self.orig_maze = maze
        self.agent = sys
        self.tester = tester
        self.timestep = 0
        self.trace = []
        self.replanned = False
        self.inv_state_map = None
        self.state_map = None
        self.node_dict = None
        self.inv_node_dict = None
        # self.state_in_G, self.G, self.node_dict = self.setup()


    def setup(self):
        G, node_dict, inv_node_dict, init, new_cuts, cuts, state_map, flow = find_cuts()
        state_in_G = init[0]
        self.node_dict = node_dict
        self.inv_node_dict = inv_node_dict
        self.state_map = state_map
        self.inv_state_map = {}
        for item in self.state_map.keys():
            self.inv_state_map.update({self.state_map[item]: item})
        return state_in_G, G, node_dict


    def agent_take_step(self):
        self.agent.agent_move(self.tester.q)

    def test_strategy(self):
        # current state in TS
        # st()
        current_state = self.inv_state_map[(self.agent.s, self.tester.q, 't')]
        out_edges = self.G.out_edges(self.state_in_G) # last state in G
        for out_edge in out_edges:
            if self.node_dict[out_edge[-1]][0] == current_state: # the system moved here
                self.state_in_G = out_edge[-1]
        # where shall the tester move
        move_options = []
        out_edges = self.G.out_edges(self.state_in_G)
        for out_edge in out_edges: # the system moved here
                move_options.append(out_edge[-1])
        move_on_G = random.choice(move_options)
        cell = self.state_map[self.node_dict[move_on_G][0]][1]
        self.tester.move(cell)

    def random_test_strategy(self):
        self.tester.random_move()

    def is_terminal(self):
        terminal = False
        if self.agent.s == self.agent.goal:
            terminal = True
        return terminal
