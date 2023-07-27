'''
Defining the grid world for the example.
Josefine Graebener
July 2023
'''
import sys
sys.path.append('..')
from ipdb import set_trace as st
import networkx as nx
from collections import OrderedDict as od


def create_network_from_file(mazefile):
    map = od()
    f = open(mazefile, 'r')
    lines = f.readlines()
    len_y = len(lines)
    for i,line in enumerate(lines):
        for j,item in enumerate(line):
            if item != '\n' and item != '|':
                map[i,j] = item
                len_x = j
    len_x += 1
    # st()
    return map, len_x, len_y


class MazeNetwork:
    def __init__(self, mazefile):
        self.init = None
        self.goal = None
        self.park = None
        self.map, self.len_x, self.len_y = create_network_from_file(mazefile)
        self.tester_init = None
        self.G_transitions, self.single_states, self.next_state_dict = self.setup_next_states_map()
        self.G = self.create_network_graph()


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

    def create_network_graph(self):
        states = []
        for x_s in range(self.len_x):
            for y_s in range(self.len_y):
                for x_t in range(self.len_x):
                    for y_t in range(self.len_y):
                        if self.map[(x_s,y_s)] != '*' and self.map[(x_t,y_t)] != '*' and y_t == 1:
                            states.append(((x_s,y_s), (x_t, y_t)))

        transitions = []
        test_transitions = []
        # adding tester actions
        next_sys_state_dict = {}
        for state in states: #tester can move according to
            next_sys_states = [(state[0], state[1])]
            for test_state in self.next_state_dict[(state[1])]:
                next_sys_states.append((state[0], test_state))
            next_sys_state_dict.update({state: next_sys_states})
        # adding system actions
        next_tester_state_dict = {}
        for state in states: #tester can move according to
            next_test_states = [(state[0], state[1])]
            for sys_state in self.next_state_dict[(state[0])]:
                next_test_states.append((sys_state, state[1]))
            next_tester_state_dict.update({state: next_test_states})

        nodes = []
        for state in states:
            if state[0] != self.goal: # once the agent reached its goal, test is over, no more transitions
                nodes.append((state[0],state[1],'s'))
                nodes.append((state[0],state[1],'t'))

        sys_nodes = []
        test_nodes = []
        for node in nodes:
            if node[-1] == 's':
                sys_nodes.append(node)
            else:
                test_nodes.append(node)

        edges = []
        for state in states:
            # st()
            if state[0] != state[1]:# and state[0] != self.goal: # collision states have no next state and when test done then done
                out_node_s = (state[0],state[1],'s')
                in_nodes_t = [(state_t[0],state_t[1],'t') for state_t in next_tester_state_dict[state]]
                for in_node_t in in_nodes_t:
                    sys_actions = []
                    if in_node_t[:2] in states:
                        sys_actions.append((out_node_s, in_node_t))
                    edges = edges + sys_actions
                out_node_t = (state[0],state[1],'t')
                in_nodes_s = [(state_s[0],state_s[1],'s') for state_s in next_sys_state_dict[state]]
                for in_node_s in in_nodes_s:
                    test_actions = []
                    if in_node_s[:2] in states:
                        test_actions.append((out_node_t, in_node_s))
                    edges = edges + test_actions
        # st()
        G = nx.DiGraph()
        G.add_nodes_from(nodes)
        G.add_edges_from(edges)
        # st()
        return G


    def setup_next_states_map(self):
        self.print_maze()

        single_states = []
        for x in range(0,self.len_x):
            for y in range(0,self.len_y):
                if self.map[(x,y)] != '*':
                    single_states.append(((x,y)))
                if self.map[(x,y)] == 'S':
                    self.init = (x,y)
                    self.map[(x,y)] = ' '
                elif self.map[(x,y)] == 'G':
                    self.goal = (x,y)
                elif self.map[(x,y)] == 'P':
                    self.park = (x,y)
                elif self.map[(x,y)] == 'T':
                    self.tester_init = (x,y)
                    self.map[(x,y)] = ' '
                elif self.map[(x,y)] == 'R':
                    self.refuel = (x,y)
                    self.map[(x,y)] = ' '

        # st()
        next_state_dict = dict()
        for node in single_states:
            next_states = [(node[0] ,node[1])]
            for a in [-1,1]:
                if (node[0] + a ,node[1]) in single_states:
                    next_states.append((node[0]+a,node[1]))
            for b in [-1,1]:
                if (node[0],node[1] + b) in single_states:
                    next_states.append((node[0],node[1]+b))
            next_state_dict.update({node: next_states})

        # make networkx graph
        G_transitions = nx.DiGraph()
        for key in next_state_dict.keys():
            for item in next_state_dict[key]:
                G_transitions.add_edge(key,item)
        return G_transitions, single_states, next_state_dict

    def transition_specs(self, x_str, y_str):
        # st()
        dynamics_spec = set()
        for ii in range(0,self.len_x):
            for jj in range(0,self.len_y):
                if not self.map[(ii,jj)] == '*':
                    next_steps_string = '('+x_str+' = '+str(ii)+' && '+y_str+' = '+str(jj)+')'
                    for item in self.next_state_dict[(ii,jj)]:
                        if item != (ii,jj):
                            next_steps_string = next_steps_string + ' || ('+x_str+' = '+str(item[0])+' && '+y_str+' = '+str(item[1])+')'
                    dynamics_spec |= {'('+x_str+' = '+str(ii)+' && '+y_str+' = '+str(jj)+') -> X(('+ next_steps_string +'))'}
                    # print('('+x_str+' = '+str(ii)+' && '+y_str+' = '+str(jj)+') -> X(('+ next_steps_string +'))')
        return dynamics_spec


if __name__ == '__main__':
    mazefile = 'maze.txt'
    maze = MazeNetwork(mazefile)
    st()
