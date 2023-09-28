import sys
sys.path.append('..')
import numpy as np
from ipdb import set_trace as st
import os
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import networkx as nx

def highlight_cuts(cuts, GD, SD, virtual, virtual_sys):
    '''
    Save an image of the graphs with the cuts highlighted.
    Make sure that the product graphs are called from flow_constraints/products.
    '''
    annot_cuts = [(GD.node_dict[cut[0]], GD.node_dict[cut[1]]) for cut in cuts]
    sys_cuts = [(GD.node_dict[cut[0]][0], GD.node_dict[cut[1]][0]) for cut in cuts]
    sys_cuts_annot = [((cut[0], q1), (cut[1], q2)) for cut in sys_cuts for q1 in virtual_sys.AP for q2 in virtual_sys.AP]

    virtual.plot_with_highlighted_edges(annot_cuts, "imgs/virtual_with_cuts")
    virtual_sys.plot_with_highlighted_edges(sys_cuts_annot, "imgs/virtual_sys_with_cuts")

def plot_flow_on_maze(maze, cuts):
    # get the max flow for the cuts
    # remove redundant cuts
    cuts = list(set(cuts))
    # find the max flow for these cuts
    G = nx.DiGraph()
    G.add_node('goal')
    for node in maze.G_single.nodes:
        G.add_node(node)

    for edge in maze.G_single.edges:
        if edge not in cuts:
            G.add_edge(edge[0],edge[1], capacity=1.0)
    for node in maze.goal:
        G.add_edge(node, 'goal', capacity=5.0) # 5 as placeholder for infty

    flow_value, flow_dict = nx.maximum_flow(G, maze.init, 'goal')

    tilesize = 1
    xs = np.linspace(0, maze.len_x*tilesize, maze.len_x+1)
    ys = np.linspace(0, maze.len_y*tilesize, maze.len_y+1)

    ax = plt.gca()
    colorstr = 'red'

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
                ax.text(x+tilesize/2, y+tilesize/2, 'I')
            elif (j,i) in maze.goal:
                ax.add_patch(Rectangle((x, y), w, h, fill=True, color='yellow', alpha=.3))
                ax.text(x+tilesize/2, y+tilesize/2, 'T')
            elif i % 2 == j % 2:
                ax.add_patch(Rectangle((x, y), w, h, fill=True, color='black', alpha=.1))
                if (j,i) == maze.init:
                    ax.text(x+tilesize/2, y+tilesize/2, 'S')
            elif maze.map[j,i]=='':
                ax.add_patch(Rectangle((x, y), w, h, fill=True, color='black', alpha=.2))
                if (j,i) == maze.init:
                    ax.text(x+tilesize/2, y+tilesize/2, 'S')
    # grid lines
    for x in xs:
        ax.plot([x, x], [ys[0], ys[-1]], color='black', alpha=.33, linestyle=':')
    for y in ys:
        ax.plot([xs[0], xs[-1]], [y, y], color='black', alpha=.33, linestyle=':')

    for cut in cuts:
        startxy = cut[0]
        endxy = cut[1]
        x_val = (startxy[0]+endxy[0])/2
        y_val = (startxy[1]+endxy[1])/2
        intensity = 1.0/2
        ax.plot([y_val+ tilesize/2, y_val+ tilesize/2], [x_val+ tilesize/2, x_val+ tilesize/2], color='black', alpha=intensity, marker='o')
        # ax.plot([xs[0], xs[-1]], [y, y], color='black', alpha=.33, linestyle=':')

    for out_node in flow_dict.keys():
        if out_node != 'goal':
            startxy = out_node
            for in_node in flow_dict[out_node]:
                if in_node != 'goal':
                    endxy = in_node
                    intensity = flow_dict[out_node][in_node]/2
                    if intensity:
                        ax.plot([startxy[1]+ tilesize/2, endxy[1]+ tilesize/2], [startxy[0]+ tilesize/2, endxy[0]+ tilesize/2], color=colorstr, alpha=intensity, linestyle='-')

    ax.invert_yaxis()
    ax.axis('equal')
    plt.show()

def plot_maze(maze):
    tilesize = 1
    xs = np.linspace(0, maze.len_x*tilesize, maze.len_x+1)
    ys = np.linspace(0, maze.len_y*tilesize, maze.len_y+1)
    ax = plt.gca()
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
                ax.text(x+tilesize/2, y+tilesize/2, 'I')
            elif (j,i) in maze.goal:
                ax.add_patch(Rectangle((x, y), w, h, fill=True, color='yellow', alpha=.3))
                ax.text(x+tilesize/2, y+tilesize/2, 'T')
            elif i % 2 == j % 2:
                ax.add_patch(Rectangle((x, y), w, h, fill=True, color='black', alpha=.1))
                if (j,i) == maze.init:
                    ax.text(x+tilesize/2, y+tilesize/2, 'S')
            elif maze.map[j,i]=='':
                ax.add_patch(Rectangle((x, y), w, h, fill=True, color='black', alpha=.2))
                if (j,i) == maze.init:
                    ax.text(x+tilesize/2, y+tilesize/2, 'S')

    # grid lines
    for x in xs:
        plt.plot([x, x], [ys[0], ys[-1]], color='black', alpha=.33, linestyle=':')
    for y in ys:
        plt.plot([xs[0], xs[-1]], [y, y], color='black', alpha=.33, linestyle=':')

    ax.invert_yaxis()
    ax.axis('equal')
    plt.show()
