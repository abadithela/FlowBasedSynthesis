# The game - consisting of the grid world layout and the system
# no dynamic tester or reactive obstacles in this implementation

from ipdb import set_trace as st
from copy import deepcopy
from find_cuts import find_cuts
import random
import _pickle as pickle
from static_examples.utils.helper import load_opt_from_pkl_file

class Game:
    def __init__(self, maze, sys):
        self.maze = deepcopy(maze)
        self.agent = sys
        self.timestep = 0
        self.trace = []
        self.setup()

    def get_optimization_results(self):
    # read pickle file - if not there save a new one
        try:
            print('Checking for the optimization results')
            cuts = load_opt_from_pkl_file()
            print('Optimization results loaded successfully')
        except:
            print('Result file not found, running optimization')
            cuts = find_cuts()
            opt_dict = {'cuts': cuts}
            with open('stored_optimization_result.p', 'wb') as pckl_file:
                pickle.dump(opt_dict, pckl_file)
        return cuts

    def setup(self):
        cuts = self.get_optimization_results()
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
