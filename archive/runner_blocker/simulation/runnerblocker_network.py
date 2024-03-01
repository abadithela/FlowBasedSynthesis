import sys
sys.path.append('..')
from ipdb import set_trace as st
import networkx as nx
# from construct_automata import get_gamegraph

class RunnerBlockerNetwork():
    def __init__(self, middle_states):
        self.source = (0,2,'s')
        self.goal = (4,1,'t')
        self.intermediate = (1,3,'t')
        self.init = self.source
        self.runner_states = [0]+[num for num in middle_states]+[4]
        self.blocker_states = [num for num in middle_states]
        self.nodes, self.edges, self.G = self.setup_G()
        # self.gamegraph, self.state_map = get_gamegraph(self)

    def state_info(self, node):
        # returns system_state, tester_state, player
        return node[0], node[1], node[2]

    def setup_G(self):
        states = []
        for run_state in self.runner_states:
            for block_state in self.blocker_states:
                states.append((run_state, block_state))

        transitions = []
        test_transitions = []
        # adding tester actions
        next_sys_state_dict = {}
        for state in states: #tester can move between m1,m2,m3
            next_sys_states = [(state[0], state[1])]
            if state[1] != self.blocker_states[-1]:
                next_sys_states.append((state[0], state[1]+1))
            if state[1] != self.blocker_states[0]:
                next_sys_states.append((state[0], state[1]-1))
            next_sys_state_dict.update({state: next_sys_states})
        # adding system actions
        next_tester_state_dict = {}
        system_moves = {0: [0,1,2,3], 1: [1,4], 2: [2,4], 3: [3,4], 4: [4]}
        for state in states:
            next_tester_states = []
            for next_sys in system_moves[state[0]]:
                next_tester_states.append((next_sys, state[1]))
            next_tester_state_dict.update({state: next_tester_states})
        # get tester acceptance states
        sys_accept = 'goal' # runner ends at goal state

        nodes = []
        for state in states:
            if state[0] != sys_accept: # once the runner reached its goal, test is over, no more transitions
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
            if state[0] != state[1] and state[0] != sys_accept: # collision states have no next state and when test done then done
                out_node_s = (state[0],state[1],'s')
                in_nodes_t = [(state_t[0],state_t[1],'t') for state_t in next_tester_state_dict[state]]
                sys_actions = [(out_node_s, in_node_t) for in_node_t in in_nodes_t]
                out_node_t = (state[0],state[1],'t')
                in_nodes_s = [(state_s[0],state_s[1],'s') for state_s in next_sys_state_dict[state]]
                test_actions = [(out_node_t, in_node_s) for in_node_s in in_nodes_s]
                edges = edges + sys_actions + test_actions

        G = nx.DiGraph()
        G.add_nodes_from(nodes)
        G.add_edges_from(edges)

        return nodes, edges, G



if __name__ == '__main__':
    network = RunnerBlockerNetwork([1,2,3])
    st()
