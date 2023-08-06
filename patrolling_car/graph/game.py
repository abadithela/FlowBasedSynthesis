'''
Game class - contains the system and tester and can be called to take the next step.
Josefine Graebener
July 2023
'''
from ipdb import set_trace as st
from copy import deepcopy
# from find_cuts import find_cuts
import random
import networkx as nx
from copy import deepcopy
from tulip.transys import transys

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
        # self.inv_node_dict = None
        self.G_cleaned = None
        self.state_in_G = None
        self.G = None
        self.acc_test = None
        self.acc_sys = []
        self.setup()
        self.G_controller = None
        self.setup_G_controller()
        # st()

    def setup(self):
        pass

    def setup_G_controller(self):
        pass

    def print_maze_with_agents(self):
        key_y_old = []
        printline = ""
        for key in self.maze.map:
            key_y_new = key[0]
            if key_y_new == key_y_old:
                # st()
                if key == (self.agent.x,self.agent.y):
                    printline += 'C'
                elif key == (self.tester.x,self.tester.y):
                    printline += 'T'
                else:
                    printline += self.maze.map[key]
            else:
                print(printline)
                if key == (self.agent.x,self.agent.y):
                    printline = 'C'
                elif key == (self.tester.x,self.tester.y):
                    printline = 'T'
                else:
                    printline = self.maze.map[key]
            key_y_old = key_y_new
        print(printline)
        printline = self.maze.map[key]

    def agent_take_step(self):
        self.agent.agent_move(self.tester.q)

    def test_strategy(self):
        # current state in TS
        # st()
        # current_state = self.inv_state_map[(self.agent.s, self.tester.q, 't')]
        if not self.state_in_G in self.acc_sys:
            current_state_s = self.inv_state_map[(self.maze.inv_mapping[self.agent.s], self.maze.inv_mapping[self.tester.q], 't')]

            # if curent_state_s in self.acc_sys:
                # pass
            out_edges = self.G_cleaned.out_edges(self.state_in_G) # last state in G
            loc_options = []
            for out_edge in out_edges:
                if str(self.node_dict[out_edge[-1]][0]) == current_state_s: # the system moved here
                    loc_options.append(out_edge[-1])
            advanced = False
            # st()
            old_state_in_G = self.state_in_G
            for option in loc_options:
                option_ok = self.node_dict[option][1][0] != self.node_dict[old_state_in_G][1][0]
                if option_ok:
                    self.state_in_G = deepcopy(option)
                    advanced = True
            if not advanced:
                self.state_in_G = loc_options[0]
            print('System - Moved to {}'.format(self.state_in_G))
        if not self.state_in_G in self.acc_sys:
            # where shall the tester move
            poss_move_options = []
            out_edges = self.G_cleaned.out_edges(self.state_in_G)
            for out_edge in out_edges:
                for acc in self.acc_test:
                    ok = False
                    if nx.has_path(self.G_cleaned,out_edge[-1],acc):
                        ok = True
                if ok:
                    poss_move_options.append(out_edge[-1])
            move_options = []
            for move in poss_move_options:
                # st()
                ok = True
                if self.state_map[self.node_dict[move][0]][0] < 2 and self.state_map[self.node_dict[move][0]][1] not in [1,9]:
                    ok = False
                elif self.state_map[self.node_dict[move][0]][0] in [2,3] and self.state_map[self.node_dict[move][0]][1] not in [3,10]:
                    ok = False
                elif self.state_map[self.node_dict[move][0]][0] in [4,5] and self.state_map[self.node_dict[move][0]][1] not in [5,11]:
                    ok = False
                elif self.state_map[self.node_dict[move][0]][0] in [6] and self.state_map[self.node_dict[move][0]][1] not in [11]:
                    ok = False
                if ok:
                    move_options.append(move)
            # st()
            if move_options == []:
                st()
            dist_dict = dict()
            for move_option in move_options:
                min_dist = min([nx.shortest_path_length(self.G_cleaned, move_option, acc) for acc in self.acc_sys])
                dist_dict.update({min_dist: move_option})
            # print(dist_dict)
            # st()
            dist = min(dist_dict.keys())
            move_on_G = random.choice([dist_dict[dist]])
            self.state_in_G = move_on_G # update move
            print('Tester - Moved to {}'.format(self.state_in_G))
        # st()

            cell = self.maze.mapping[self.state_map[self.node_dict[move_on_G][0]][1]][0]
            self.tester.move(cell)
        else:
            print('Reached goal - tester waits')

    def random_test_strategy(self):
        self.tester.random_move(self.agent.s)

    def is_terminal(self):
        terminal = False
        if self.agent.s == self.agent.goal:
            terminal = True
        return terminal
