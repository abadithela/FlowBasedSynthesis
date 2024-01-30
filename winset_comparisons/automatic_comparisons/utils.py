# import sys
# sys.path.append('..')
import sys
sys.path.append('../..')
from components.maze_network import MazeNetwork, create_network_from_file
from components.plotting import plot_maze
import networkx as nx
from ipdb import set_trace as st
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Wedge
import datetime

def make_comparison_plots(output, maze, flow_cuts):
    fig, ax = plt.subplots(nrows=1, ncols=2)

    synth_cuts = []
    for edge in maze.graph.edges:
        namestr = 'edge'+str(edge[0][0])+str(edge[0][1])+'_'+str(edge[1][0])+str(edge[1][1])
        if output[namestr] == 1:
            synth_cuts.append(edge)

    cuts = {0: synth_cuts, 1: flow_cuts}
    titles = {0: 'Synthesis', 1: 'Flows'}

    tilesize = 1
    xs = np.linspace(0, maze.len_x*tilesize, maze.len_x+1)
    ys = np.linspace(0, maze.len_y*tilesize, maze.len_y+1)

    # fig, ax = plt.subplots()
    # st()
    for k in range(len(ax)):
        ax[k].xaxis.set_visible(False)
        ax[k].yaxis.set_visible(False)
        # grid "shades" (boxes)
        w, h = xs[1] - xs[0], ys[1] - ys[0]
        for i, x in enumerate(xs[:-1]):
            for j, y in enumerate(ys[:-1]):
                if maze.map[j,i]=='*':
                    ax[k].add_patch(Rectangle((x, y), w, h, fill=True, color='black', alpha=.5))
                elif (j,i) in maze.int:
                    ax[k].add_patch(Rectangle((x, y), w, h, fill=True, color='blue', alpha=.3))
                    ax[k].text(x+tilesize/2, y+tilesize/2, maze.int[(j,i)])
                elif (j,i) in maze.goal:
                    ax[k].add_patch(Rectangle((x, y), w, h, fill=True, color='yellow', alpha=.3))
                    ax[k].text(x+tilesize/2, y+tilesize/2, 'T')

                elif i % 2 == j % 2:
                    ax[k].add_patch(Rectangle((x, y), w, h, fill=True, color='black', alpha=.1))
                    if (j,i) == maze.init:
                        ax[k].text(x+tilesize/2, y+tilesize/2, 'S')
                    elif (j,i) in maze.unsafe:
                        ax[k].text(x+tilesize/2, y+tilesize/2, 'U')
                    elif (j,i) in maze.deadends:
                        ax[k].text(x+tilesize/2, y+tilesize/2, 'D')
                else:
                    ax[k].add_patch(Rectangle((x, y), w, h, fill=True, color='white', alpha=.2))
                    if (j,i) == maze.init:
                        ax[k].text(x+tilesize/2, y+tilesize/2, 'S')
                    elif (j,i) in maze.unsafe:
                        ax[k].text(x+tilesize/2, y+tilesize/2, 'U')
                    elif (j,i) in maze.deadends:
                        ax[k].text(x+tilesize/2, y+tilesize/2, 'D')

        # grid lines
        for x in xs:
            ax[k].plot([x, x], [ys[0], ys[-1]], color='black', alpha=.33, linestyle=':')
        for y in ys:
            ax[k].plot([xs[0], xs[-1]], [y, y], color='black', alpha=.33, linestyle=':')

        width = tilesize/20
        for cut in cuts[k]:
            startxy = cut[0]
            endxy = cut[1]
            delx = startxy[0] - endxy[0]
            dely = startxy[1] - endxy[1]
            if delx == 0:
                if dely < 0:
                    ax[k].add_patch(Rectangle((startxy[1]- width/2 - dely*tilesize , startxy[0] - width/2), width, tilesize+width, fill=True, color='black', alpha=1.0))
                else:
                    ax[k].add_patch(Rectangle((startxy[1]- width/2 , startxy[0]- width/2), width, tilesize+width, fill=True, color='black', alpha=1.0))
            elif dely == 0:
                if delx < 0:
                    ax[k].add_patch(Rectangle((startxy[1]- width/2, startxy[0]- width/2 - delx*tilesize), tilesize+width, width, fill=True, color='black', alpha=1.0))
                else:
                    ax[k].add_patch(Rectangle((startxy[1]- width/2, startxy[0]- width/2), tilesize + width, width, fill=True, color='black', alpha=1.0))

        ax[k].invert_yaxis()
        ax[k].axis('equal')
        ax[k].set_title(titles[k])
    plt.show()
    now = str(datetime.datetime.now())
    fig.savefig('comparison'+now+'.pdf')


def get_test_vars(maze):
    test_vars = {}
    for edge in maze.graph.edges:
        # namestr = 'edge'+str(edge[0])+'_'+str(edge[1])
        namestr = 'edge'+str(edge[0][0])+str(edge[0][1])+'_'+str(edge[1][0])+str(edge[1][1])
        test_vars[namestr] = (0,1)
    return test_vars

def get_test_init(maze):
    test_init = set()
    for edge in maze.graph.edges:
        namestr = 'edge'+str(edge[0][0])+str(edge[0][1])+'_'+str(edge[1][0])+str(edge[1][1])
        test_init |= {'('+namestr+' = 0 || '+namestr+' = 1)'}
    return test_init

def get_test_safety_static(maze):
    test_safety = set()
    for edge in maze.graph.edges:
        namestr = 'edge'+str(edge[0][0])+str(edge[0][1])+'_'+str(edge[1][0])+str(edge[1][1])
        test_safety |= {namestr + ' = 0 -> X('+namestr+' = 0)'}
        test_safety |= {namestr + ' = 1 -> X('+namestr+' = 1)'}
    return test_safety

def relate_edge_cuts_to_system_moves(maze):
    safe_spec = set()
    from ipdb import set_trace as st
    for edge in maze.graph.edges:
        namestr = 'edge'+str(edge[0][0])+str(edge[0][1])+'_'+str(edge[1][0])+str(edge[1][1])
        safe_spec |= {'(z = '+str(edge[0][0])+' && x = '+str(edge[0][1])+' && '+namestr+' = 1) -> X(!(z = '+str(edge[1][0])+' && x = '+str(edge[1][1])+'))'}
        safe_spec |= {'(z = '+str(edge[1][0])+' && x = '+str(edge[1][1])+' && '+namestr+' = 1) -> X(!(z = '+str(edge[0][0])+' && x = '+str(edge[0][1])+'))'}
    return safe_spec

def plot_sol(sol_dict, maze):
    cuts = []
    for edge in maze.graph.edges:
        namestr = 'edge'+str(edge[0][0])+str(edge[0][1])+'_'+str(edge[1][0])+str(edge[1][1])
        if sol_dict[namestr] == 1:
            cuts.append(edge)

    tilesize = 1
    xs = np.linspace(0, maze.len_x*tilesize, maze.len_x+1)
    ys = np.linspace(0, maze.len_y*tilesize, maze.len_y+1)

    fig, ax = plt.subplots()

    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    # grid "shades" (boxes)
    w, h = xs[1] - xs[0], ys[1] - ys[0]
    for i, x in enumerate(xs[:-1]):
        for j, y in enumerate(ys[:-1]):
            if maze.map[j,i]=='*':
                ax.add_patch(Rectangle((x, y), w, h, fill=True, color='black', alpha=.5))
            elif (j,i) in maze.int:
                ax.add_patch(Rectangle((x, y), w, h, fill=True, color='blue', alpha=.3))
                ax.text(x+tilesize/2, y+tilesize/2, maze.int[(j,i)])
            elif (j,i) in maze.goal:
                ax.add_patch(Rectangle((x, y), w, h, fill=True, color='yellow', alpha=.3))
                ax.text(x+tilesize/2, y+tilesize/2, 'T')

            elif i % 2 == j % 2:
                ax.add_patch(Rectangle((x, y), w, h, fill=True, color='black', alpha=.1))
                if (j,i) == maze.init:
                    ax.text(x+tilesize/2, y+tilesize/2, 'S')
                elif (j,i) in maze.unsafe:
                    ax.text(x+tilesize/2, y+tilesize/2, 'U')
                elif (j,i) in maze.deadends:
                    ax.text(x+tilesize/2, y+tilesize/2, 'D')
            else:
                ax.add_patch(Rectangle((x, y), w, h, fill=True, color='white', alpha=.2))
                if (j,i) == maze.init:
                    ax.text(x+tilesize/2, y+tilesize/2, 'S')
                elif (j,i) in maze.unsafe:
                    ax.text(x+tilesize/2, y+tilesize/2, 'U')
                elif (j,i) in maze.deadends:
                    ax.text(x+tilesize/2, y+tilesize/2, 'D')

    # grid lines
    for x in xs:
        plt.plot([x, x], [ys[0], ys[-1]], color='black', alpha=.33, linestyle=':')
    for y in ys:
        plt.plot([xs[0], xs[-1]], [y, y], color='black', alpha=.33, linestyle=':')

    i = 1
    width = tilesize/20
    for cut in cuts:
        startxy = cut[0]
        endxy = cut[1]
        delx = startxy[0] - endxy[0]
        dely = startxy[1] - endxy[1]
        if delx == 0:
            if dely < 0:
                ax.add_patch(Rectangle((startxy[1]- width/2 - dely*tilesize , startxy[0] - width/2), width, tilesize+width, fill=True, color='black', alpha=1.0))
            else:
                ax.add_patch(Rectangle((startxy[1]- width/2 , startxy[0]- width/2), width, tilesize+width, fill=True, color='black', alpha=1.0))
        elif dely == 0:
            if delx < 0:
                ax.add_patch(Rectangle((startxy[1]- width/2, startxy[0]- width/2 - delx*tilesize), tilesize+width, width, fill=True, color='black', alpha=1.0))
            else:
                ax.add_patch(Rectangle((startxy[1]- width/2, startxy[0]- width/2), tilesize + width, width, fill=True, color='black', alpha=1.0))

    ax.invert_yaxis()
    ax.axis('equal')
    plt.show()
    fig.savefig("maze.pdf")


class AugMazeNetwork(MazeNetwork):
    def __init__(self, mazefile, obs = []):
        MazeNetwork.__init__(self, mazefile, obs = [])
        self.unsafe = []
        self.deadends = []
        self.intermed = []
        self.graph = self.create_graph()
        self.setup_states()

    def setup_states(self):
        for z in range(0,self.len_z):
            for x in range(0,self.len_x):
                if self.map[(z,x)] != '*':
                    if self.map[(z,x)] == 'S':
                        self.init = (z,x)
                    if self.map[(z,x)] == 'T':
                        self.goal.append((z,x))
                    if self.map[(z,x)] == 'U':
                        self.unsafe.append((z,x))
                    if self.map[(z,x)] == 'D':
                        self.deadends.append((z,x))
                    if self.map[(z,x)] == 'I':
                        self.intermed.append((z,x))
        self.int = {pos: 'I' for pos in self.intermed}

    def augmented_dynamics_specs(self, x_str, z_str):
        dynamics_spec = set()
        for ii in range(0,self.len_z):
            for jj in range(0,self.len_x):
                if not self.map[(ii,jj)] == '*':
                    next_steps_string = '('+z_str+' = '+str(ii)+' && '+x_str+' = '+str(jj)+')'
                    if (ii,jj) not in self.deadends:
                        for item in self.next_state_dict[(ii,jj)]:
                            if item != (ii,jj):
                                next_steps_string = next_steps_string + ' || ('+z_str+' = '+str(item[0])+' && '+x_str+' = '+str(item[1])+')'
                        dynamics_spec |= {'('+z_str+' = '+str(ii)+' && '+x_str+' = '+str(jj)+') -> X(('+ next_steps_string +'))'}
        return dynamics_spec

    def create_graph(self):
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
            if state not in self.deadends:
                for sys_state in self.next_state_dict[(state)]:
                    next_states.append((sys_state))
            next_state_dict.update({state: next_states})

        nodes = []
        nodes = states

        edges = []
        for state in states:
            # if state not in self.goal: # when test done then done
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

        to_remove = []
        for i, j in G.edges:
            if i == j:
                to_remove.append((i,j))
        G.remove_edges_from(to_remove)

        return G
