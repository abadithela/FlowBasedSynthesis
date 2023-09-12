import sys
sys.path.append('..')
from ipdb import set_trace as st
import networkx as nx
from collections import OrderedDict as od


def create_network_from_file(mazefile):
    map = od()
    f = open(mazefile, 'r')
    lines = f.readlines()
    len_z = len(lines)
    for i,line in enumerate(lines):
        for j,item in enumerate(line):
            if item != '\n' and item != '|':
                map[i,j] = item
                len_x = j
    len_x += 1
    # st()
    return map, len_x, len_z

class MazeNetwork:
    def __init__(self, mazefile):
        self.init = None
        self.goal = None
        self.int = None
        self.map, self.len_x, self.len_z = create_network_from_file(mazefile)
        self.len_y = self.len_z
        self.tester_init = (6,2)
        self.G_transitions, self.single_states, self.next_state_dict = self.setup_next_states_map()
        self.G_single = self.create_single_agent_graph()

    def set_int(self, int):
        self.int = int

    def set_goal(self,goal):
        self.goal = goal

    def state_info(self, node):
        # returns system_state, tester_state, player
        return node[0], node[1], node[2]

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

    def create_single_agent_graph(self):
        states = []
        for x_s in range(self.len_x):
            for z_s in range(self.len_z):
                if self.map[(z_s,x_s)] != '*':
                    states.append((z_s,x_s))

        transitions = []
        # adding system actions
        next_state_dict = {}
        for state in states: #tester can move according to
            next_states = [(state)]
            for sys_state in self.next_state_dict[(state)]:
                next_states.append((sys_state))
            next_state_dict.update({state: next_states})

        nodes = []
        nodes = states

        edges = []
        for state in states:
            # if state != self.goal: # collision states have no next state and when test done then done
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
        return G

    def setup_next_states_map(self):
        self.print_maze()

        single_states = []
        for z in range(0,self.len_z):
            for x in range(0,self.len_x):
                if self.map[(z,x)] != '*':
                    single_states.append(((z,x)))
                    if self.map[(z,x)] == 'S':
                        self.init = (z,x)
                    # if (z,x) == (0,0):
                    #     self.goal = (z,x)

        next_state_dict = dict()
        for node in single_states:
            next_states = [(node[0], node[1])]
            if node != self.goal:
                for a in [-1,1]: # can always move horizontally!
                    if (node[0],node[1]+a) in single_states:
                        next_states.append((node[0], node[1]+a))
                for b in [-1,1]: # can always move vertically!
                    if (node[0]+b,node[1]) in single_states:
                        next_states.append((node[0]+b, node[1]))
            next_state_dict.update({node: next_states})

        # make networkx graph
        G_transitions = nx.DiGraph()
        for key in next_state_dict.keys():
            for item in next_state_dict[key]:
                G_transitions.add_edge(key,item)
        return G_transitions, single_states, next_state_dict


    def transition_specs(self, z_str, y_str):
        # st()
        dynamics_spec = set()
        for ii in range(0,self.len_z):
            for jj in range(0,self.len_x):
                if not self.map[(ii,jj)] == '*':
                    next_steps_string = '('+z_str+' = '+str(ii)+' && '+y_str+' = '+str(jj)+')'
                    for item in self.next_state_dict[(ii,jj)]:
                        if item != (ii,jj):
                            next_steps_string = next_steps_string + ' || ('+z_str+' = '+str(item[0])+' && '+y_str+' = '+str(item[1])+')'
                    dynamics_spec |= {'('+z_str+' = '+str(ii)+' && '+y_str+' = '+str(jj)+') -> X(('+ next_steps_string +'))'}
        return dynamics_spec


if __name__ == '__main__':
    mazefile = 'maze.txt'
    maze = MazeNetwork(mazefile)
    st()
