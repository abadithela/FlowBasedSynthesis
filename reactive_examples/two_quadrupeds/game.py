from ipdb import set_trace as st
from copy import deepcopy
from find_cuts import find_cuts
import random
import _pickle as pickle
from reactive_examples.utils.helper import load_opt_from_pkl_file
from reactive_examples.utils.quadruped_interface import quadruped_move
from parse_opt_constraints import MapConstraints

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
        self.turn = 'sys'
        # self.state_in_G, self.G, self.node_dict = self.setup()
        self.setup()

    def get_optimization_results(self):
    # read pickle file - if not there save a new one
        try:
            print('Checking for the optimization results')
            cuts, GD, SD = load_opt_from_pkl_file()
            print('Optimization results loaded successfully')
        except:
            print('Result file not found, running optimization')
            cuts, GD, SD = find_cuts()
            opt_dict = {'cuts': cuts, 'GD': GD, 'SD': SD}
            with open('stored_optimization_result.p', 'wb') as pckl_file:
                pickle.dump(opt_dict, pckl_file)
        return cuts, GD, SD

    def setup(self):
        cuts, GD, SD = self.get_optimization_results()
        map_constraints = MapConstraints(cuts, GD, SD)
        cuts = map_constraints.cuts_with_dynamic_agent
        st()
        # cuts = [(((2, 2), 'q12'), ((1, 2), 'q12')), (((4, 2), 'q15'), ((3, 2), 'q15')), (((6, 2), 'q0'), ((5, 2), 'q0'))]

        self.agent.find_controller(self.maze)
        self.tester.set_optimization_results(cuts, GD)
        self.tester.find_controller()

    def print_game_state(self):
        z_old = []
        printline = ""
        for key in self.maze.map:
            z_new = key[0]
            if self.agent.s == key:
                add_str = 'S'
            elif self.tester.q == key:
                add_str = 'T'
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
        self.agent.agent_move(self.tester.q)
        quadruped_move('system', (self.agent.z,self.agent.x))

    def tester_take_step(self):
        # the tester move will stay the same here but the turn will update
        self.tester.tester_move(self.agent.s)
        # now the tester moves
        self.tester.tester_move(self.agent.s)
        quadruped_move('tester', (self.tester.z,self.tester.x))

    def is_terminal(self):
        terminal = False
        if self.agent.s == self.agent.goal:
            terminal = True
        return terminal
