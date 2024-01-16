# The game - consisting of the grid world layout and the system
# no dynamic tester or reactive obstacles in this implementation

from ipdb import set_trace as st
from copy import deepcopy
from find_cuts import find_cuts
import random

class Game:
    def __init__(self, maze, sys):
        self.maze = deepcopy(maze)
        self.agent = sys
        self.timestep = 0
        self.trace = []
        self.setup()

    def setup(self):
        cuts = find_cuts()
        # st()
        cuts = list(set(cuts))
        for cut in cuts:
            self.maze.add_cut(cut)
        self.agent.find_controller(self.maze)

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

    def is_terminal(self):
        terminal = False
        if self.agent.s in self.agent.goals:
            terminal = True
        return terminal
