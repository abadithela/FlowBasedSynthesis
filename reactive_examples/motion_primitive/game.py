from ipdb import set_trace as st
from copy import deepcopy
from find_cuts import find_cuts
import sys
sys.path.append('..')
# from helpers.helper import load_opt_from_pkl_file
import _pickle as pickle
from utils.quadruped_interface import quadruped_move
from problem_data import *

class Game:
    def __init__(self, maze, agent):
        self.maze = deepcopy(maze)
        self.orig_maze = maze
        self.agent = agent
        self.timestep = 0
        self.trace = []
        self.replanned = False
        self.agent_in_state_x = None
        self.cuts = []
        self.GD = None
        self.SD = None
        self.setup()

    def setup(self):
        print('Setting up graphs, Running optimization')
        self.cuts, self.GD, self.SD = find_cuts(self.maze)
        self.graph_cuts = [(self.GD.inv_node_dict[cut[0]], self.GD.inv_node_dict[cut[1]]) for cut in self.cuts]
        self.agent_in_state_x = self.GD.init[0]

    def agent_take_step(self):
        cur_s = self.agent.s
        output = self.agent.controller.move()
        next_s = self.maze.map[output['s']]

        # if cur_s == 'int_goal':
        #     next_s = 'p2'
        #     self.agent.s = next_s
        #     self.agent.find_controller(self.agent.s)
        # else:
        #     output = self.agent.controller.move()
        #     next_s = self.maze.map[output['s']]

        # update the tracking in G
        succs = self.GD.graph[self.agent_in_state_x]

        if next_s == self.GD.node_dict[self.agent_in_state_x][0]:
            new_agent_in_state_x = self.agent_in_state_x
        else:
            for node in succs:
                if self.GD.node_dict[node][0] == next_s:
                    new_agent_in_state_x = node

            if (self.agent_in_state_x, new_agent_in_state_x) in self.graph_cuts:
                self.agent.set_maze(self.maze)
                self.agent.find_controller(self.agent.s)
                output = self.agent.controller.move()
                next_s = self.maze.map[output['s']]
                if next_s == self.GD.node_dict[self.agent_in_state_x][0]:
                    new_agent_in_state_x = self.agent_in_state_x
                else:
                    for node in succs:
                        if self.GD.node_dict[node][0] == next_s:
                            new_agent_in_state_x = node

        # update position
        self.agent_in_state_x = new_agent_in_state_x
        self.agent.s = next_s

        print('Agent moving to {}'.format(self.agent.s))
        quadruped_move('system', MAP[self.agent.s])


    def test_strategy(self):
        for cut in self.graph_cuts:
            if self.agent_in_state_x == cut[0]:
                cut_in_maze = (self.GD.node_dict[cut[0]][0], self.GD.node_dict[cut[1]][0])
                if cut_in_maze not in self.maze.active_cuts:
                    self.maze.add_cut(cut_in_maze)
                    print('Added cut {}'.format(cut_in_maze))


    def drop_obstacle(self, cut):
        self.maze.add_cut(cut)

    def lift_obstacles(self):
        self.maze.remove_all_cuts()

    def is_terminal(self):
        terminal = False
        if self.agent.s in self.agent.goals:
            terminal = True
        return terminal
