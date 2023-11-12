from ipdb import set_trace as st
from copy import deepcopy
# from find_cuts import find_cuts
import random

class Game:
    def __init__(self, maze, sys, GD, cuts):
        self.maze = deepcopy(maze)
        self.orig_maze = maze
        self.agent = sys
        self.GD = GD
        self.agent_state_in_G = GD.init[0]
        self.q = self.GD.node_dict[self.agent_state_in_G][-1]
        self.timestep = 0
        self.trace = []
        self.replanned = False
        # self.inv_state_map = None
        # self.state_map = None
        # self.node_dict = None
        # self.inv_node_dict = None
        self.cuts = cuts
        # self.active_cuts = []

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


    def print_game_state(self):
        z_old = []
        printline = ""
        for key in self.maze.map:
            z_new = key[0]
            if self.agent.s == key:
                add_str = 'S'
            else:
                add_str = self.maze.map[key]

            if z_new == z_old:
                printline += add_str
            else:
                print(printline)
                printline = add_str
            z_old = z_new
        print(printline)
        printline = self.maze.map[key]


    def agent_take_step(self):
        self.agent.agent_move()
        succs = self.GD.graph[self.agent_state_in_G]
        for node in succs:
            if self.GD.node_dict[node][0] == self.agent.s:
                self.agent_state_in_G = node
                q_new = self.GD.node_dict[node][-1]

        if self.q != q_new:
            self.lift_obstacles()

        self.q = q_new


    def test_strategy(self):
        for cut in self.cuts:
            if self.GD.node_dict[self.agent_state_in_G] == cut[0]:
                cut_a = cut[0][0]
                cut_b = cut[1][0]
                if cut_b in self.maze.next_state_dict[cut_a]:
                    self.drop_obstacle((cut_a,cut_b))
                    print('Obstacle placed!')
                    self.agent.controller = self.agent.find_controller(self.maze)


    def drop_obstacle(self, cut):
        self.maze.add_cut(cut)
        # self.active_cuts.append(cut)

    def lift_obstacles(self):
        print('Lifting obstacles!')
        self.maze.remove_all_cuts()
        # self.active_cuts = []

    def is_terminal(self):
        terminal = False
        if self.agent.s == self.agent.goal:
            terminal = True
        return terminal
