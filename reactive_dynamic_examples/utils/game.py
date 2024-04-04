from ipdb import set_trace as st
from copy import deepcopy
from find_cuts import find_cuts, find_graphs, solve_opt
import random
import time
import _pickle as pickle
from reactive_dynamic_examples.utils.helper import load_opt_from_pkl_file
from reactive_dynamic_examples.utils.quadruped_interface import quadruped_move
from reactive_dynamic_examples.utils.parse_cuts import Map_Reactive_Cuts
from reactive_dynamic_examples.utils.setup_logger import setup_logger

from problem_data import *

class Game:
    def __init__(self, maze, sys, tester, logger=None):
        self.maze = deepcopy(maze)
        self.orig_maze = maze
        self.agent = sys
        self.tester = tester
        self.logger = logger
        self.timestep = 0
        self.trace = []
        self.replanned = False
        self.inv_state_map = None
        self.state_map = None
        self.node_dict = None
        self.inv_node_dict = None
        self.turn = 'sys'
        # self.state_in_G, self.G, self.node_dict = self.setup()
        # self.setup()
        self.setup_cex()

    def get_optimization_results(self, logger = None):
    # read pickle file - if not there save a new one
        try:
            print('Checking for the optimization results')
            cuts, GD, SD = load_opt_from_pkl_file()
            print('Optimization results loaded successfully')
        except:
            print('Result file not found, running optimization')
            cuts, GD, SD = find_cuts(logger = self.logger)#logger=self.logger)
            opt_dict = {'cuts': cuts, 'GD': GD, 'SD': SD}
            with open('stored_optimization_result.p', 'wb') as pckl_file:
                pickle.dump(opt_dict, pckl_file)
        return cuts, GD, SD

    def setup(self):
        cuts, GD, SD = self.get_optimization_results()
        static_cuts = list(set([(cut[0][0], cut[1][0]) for cut in cuts if cut[0][0] in STATIC_AREA and cut[1][0] in STATIC_AREA]))

        for cut in static_cuts:
            self.maze.add_cut_w_fuel(cut)

        self.agent.find_controller(self.maze)
        self.tester.set_optimization_results(cuts, GD, SD)
        self.tester.find_controller()


    def setup_cex(self, load_sol = False):
        self.logger = setup_logger("quadruped_plus")
        # Solving optimization with counterexample guided search.
        strategy_found = False
        excluded_sols = []

        if not load_sol:
            virtual, system, b_pi, virtual_sys = find_graphs(logger = self.logger)

        while not strategy_found:
            # solve optimization
            if load_sol:
                cuts, GD, SD = self.get_optimization_results(logger = self.logger)
            else:
                cuts, GD, SD = solve_opt(virtual, system, b_pi, virtual_sys, logger = self.logger, excluded_sols = excluded_sols)

            graph_cuts = [(GD.inv_node_dict[cut[0]], GD.inv_node_dict[cut[1]]) for cut in cuts]

            # synthesize controller
            static_cuts = list(set([(cut[0][0], cut[1][0]) for cut in cuts if cut[0][0] in STATIC_AREA and cut[1][0] in STATIC_AREA]))
            self.maze.reset_maze()
            for cut in static_cuts:
                try:
                    self.maze.add_cut_w_fuel(cut)
                except:
                    print("Issue with maze cuts")
                    st()
            # self.agent.find_controller(self.maze)
            self.tester.set_optimization_results(cuts, GD, SD)
            try:
                t0 = time.time()
                self.tester.find_controller(load_sol = False)
                tf = time.time()
                self.logger.save_runtime("Tester Controller RT", tf-t0)
                self.logger.save_data("Times resynthesized by CEx search: ", len(excluded_sols))
                self.agent.find_controller(self.maze)
                strategy_found = True
                print("Test Agent Strategy synthesized!.")
            except:
                excluded_sols.append(graph_cuts)
                n_exc = len(excluded_sols)
                print("!! Could not synthesize test agent strategy!!")
                print(f"Re-solving optimization with {n_exc} solutions excluded.")
                st()
        # Writing to file:
        self.logger.print_runtime_latex()
        self.logger.print_problem_data_latex()
        self.logger.print_table(dynamic=True)

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

    def agent_take_step_augmented(self):
        output = self.agent.controller.move()
        next_x = output['x']
        next_z = output['z']
        if not (next_z,next_x) == self.tester.q:
            print('Agent moving to {}'.format((next_z,next_x)))
            self.agent.x = next_x
            self.agent.z = next_z
            self.agent.s = (next_z,next_x)
        else:
            # resynthesize controller and add the blocked state!
            unsafe = (next_z,next_x)
            self.agent.resynthesize_controller(unsafe)
        quadruped_move('system', (self.agent.z,self.agent.x))

    def agent_take_step_augmented_fuel(self):
        output = self.agent.controller.move()
        next_x = output['x']
        next_z = output['z']
        next_f = output['f']
        if not (next_z,next_x) == self.tester.q:
            print('System moving to {0} - fuel {1}'.format((next_z,next_x), next_f))
            self.agent.x = next_x
            self.agent.z = next_z
            self.agent.f = next_f
            self.agent.s = (next_z,next_x)
        else:
            # resynthesize controller and add the blocked state!
            unsafe = (next_z,next_x)
            self.agent.resynthesize_controller(unsafe)
        quadruped_move('system', (self.agent.z,self.agent.x))

    def agent_take_manual_step(self):
        sys_z = input("system z: ")
        sys_x = input("system x: " )
        sys_pos = (int(sys_z), int(sys_x))
        self.agent.agent_manual_move(sys_pos)
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
