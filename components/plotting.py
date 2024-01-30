import sys
sys.path.append('..')
import numpy as np
from ipdb import set_trace as st
import os
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Wedge
import networkx as nx
import datetime

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

def plot_flow_on_maze(maze, cuts, num_int=1):
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

    flow_value, flow_dict = nx.maximum_flow(G, maze.init[0], 'goal')

    tilesize = 1
    xs = np.linspace(0, maze.len_x*tilesize, maze.len_x+1)
    ys = np.linspace(0, maze.len_y*tilesize, maze.len_y+1)

    fig, ax = plt.subplots()
    colorstr = 'red'

    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    # grid "shades" (boxes)
    w, h = xs[1] - xs[0], ys[1] - ys[0]
    for i, x in enumerate(xs[:-1]):
        for j, y in enumerate(ys[:-1]):
            if num_int==1:
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
                    if (j,i) in maze.init:
                        ax.text(x+tilesize/2, y+tilesize/2, 'S')
                elif maze.map[j,i]==' ':
                    ax.add_patch(Rectangle((x, y), w, h, fill=True, color='black', alpha=.2))
                    if (j,i) in maze.init:
                        ax.text(x+tilesize/2, y+tilesize/2, 'S')
            elif num_int==2:
                if maze.map[j,i]=='*':
                    ax.add_patch(Rectangle((x, y), w, h, fill=True, color='black', alpha=.5))
                elif (j,i) == maze.int_1:
                    ax.add_patch(Rectangle((x, y), w, h, fill=True, color='blue', alpha=.3))
                    ax.text(x+tilesize/2, y+tilesize/2, 'I1')
                elif (j,i) == maze.int_2:
                    ax.add_patch(Rectangle((x, y), w, h, fill=True, color='blue', alpha=.3))
                    ax.text(x+tilesize/2, y+tilesize/2, 'I2')
                elif (j,i) == maze.goal:
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

    # for out_node in flow_dict.keys():
    #     if out_node != 'goal':
    #         startxy = out_node
    #         for in_node in flow_dict[out_node]:
    #             if in_node != 'goal':
    #                 endxy = in_node
    #                 intensity = flow_dict[out_node][in_node]/2
    #                 if intensity:
    #                     ax.plot([startxy[1]+ tilesize/2, endxy[1]+ tilesize/2], [startxy[0]+ tilesize/2, endxy[0]+ tilesize/2], color=colorstr, alpha=intensity, linestyle='-')

    ax.invert_yaxis()
    ax.axis('equal')
    plt.show()
    now = str(datetime.datetime.now())
    fig.savefig('imgs/maze_implementation'+ now +'.pdf')

def plot_flow_soln_on_maze(maze, cuts, flow, num_int=1):
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

    flow_value, flow_dict = nx.maximum_flow(G, maze.init[0], 'goal')

    tilesize = 1
    xs = np.linspace(0, maze.len_x*tilesize, maze.len_x+1)
    ys = np.linspace(0, maze.len_y*tilesize, maze.len_y+1)

    fig, ax = plt.subplots()
    colorstr = 'red'

    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    # grid "shades" (boxes)
    w, h = xs[1] - xs[0], ys[1] - ys[0]
    for i, x in enumerate(xs[:-1]):
        for j, y in enumerate(ys[:-1]):
            if num_int==1:
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
                    if (j,i) in maze.init:
                        ax.text(x+tilesize/2, y+tilesize/2, 'S')
                elif maze.map[j,i]==' ':
                    ax.add_patch(Rectangle((x, y), w, h, fill=True, color='black', alpha=.2))
                    if (j,i) in maze.init:
                        ax.text(x+tilesize/2, y+tilesize/2, 'S')
            elif num_int==2:
                if maze.map[j,i]=='*':
                    ax.add_patch(Rectangle((x, y), w, h, fill=True, color='black', alpha=.5))
                elif (j,i) == maze.int_1:
                    ax.add_patch(Rectangle((x, y), w, h, fill=True, color='blue', alpha=.3))
                    ax.text(x+tilesize/2, y+tilesize/2, 'I1')
                elif (j,i) == maze.int_2:
                    ax.add_patch(Rectangle((x, y), w, h, fill=True, color='blue', alpha=.3))
                    ax.text(x+tilesize/2, y+tilesize/2, 'I2')
                elif (j,i) == maze.goal:
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
    fig.savefig("imgs/maze_implementation.pdf")

def plot_flow_w_colored_cuts_on_maze(maze, cuts):
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
            try:
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
                elif maze.map[j,i]=='':
                    ax.add_patch(Rectangle((x, y), w, h, fill=True, color='black', alpha=.2))
                    if (j,i) == maze.init:
                        ax.text(x+tilesize/2, y+tilesize/2, 'S')
            except:
                if maze.map[j,i]=='*':
                    ax.add_patch(Rectangle((x, y), w, h, fill=True, color='black', alpha=.5))
                elif (j,i) in maze.int_1:
                    ax.add_patch(Rectangle((x, y), w, h, fill=True, color='blue', alpha=.3))
                    ax.text(x+tilesize/2, y+tilesize/2, 'I1')
                elif (j,i) in maze.int_2:
                    ax.add_patch(Rectangle((x, y), w, h, fill=True, color='blue', alpha=.3))
                    ax.text(x+tilesize/2, y+tilesize/2, 'I2')
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

def plot_maze(maze, cuts = []):
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
            elif maze.map[j,i]=='':
                ax.add_patch(Rectangle((x, y), w, h, fill=True, color='black', alpha=.2))
                if (j,i) == maze.init:
                    ax.text(x+tilesize/2, y+tilesize/2, 'S')

    # grid lines
    for x in xs:
        plt.plot([x, x], [ys[0], ys[-1]], color='black', alpha=.33, linestyle=':')
    for y in ys:
        plt.plot([xs[0], xs[-1]], [y, y], color='black', alpha=.33, linestyle=':')

    for cut in cuts:
        startxy = cut[0]
        endxy = cut[1]
        x_val = (startxy[0]+endxy[0])/2
        y_val = (startxy[1]+endxy[1])/2
        intensity = 1.0/2
        ax.plot([y_val+ tilesize/2, y_val+ tilesize/2], [x_val+ tilesize/2, x_val+ tilesize/2], color='black', alpha=intensity, marker='o')
        # ax.plot([xs[0], xs[-1]], [y, y], color='black', alpha=.33, linestyle=':')


    ax.invert_yaxis()
    ax.axis('equal')
    plt.show()
    fig.savefig("imgs/maze.pdf")

def make_history_plots(cuts, GD, maze):
    cuts_info = [(GD.node_dict[i], GD.node_dict[j]) for (i,j) in cuts]

    qs = list(set([item[0][-1] for item in cuts_info]))

    num_panels = len(qs)

    tilesize = 1
    xs = np.linspace(0, maze.len_x*tilesize, maze.len_x+1)
    ys = np.linspace(0, maze.len_y*tilesize, maze.len_y+1)
    w, h = xs[1] - xs[0], ys[1] - ys[0]

    if num_panels > 1:
        fig, axs = plt.subplots(1,num_panels)
        fig.suptitle('Reactive Constraints')

        for k,q in enumerate(qs):
            axs[k].xaxis.set_visible(False)
            axs[k].yaxis.set_visible(False)
            axs[k].set_xlim(xs[0], xs[-1])
            axs[k].set_ylim(ys[0], ys[-1])

            # draw the grid
            for i, x in enumerate(xs[:-1]):
                for j, y in enumerate(ys[:-1]):

                    if maze.map[j,i]=='*':
                        axs[k].add_patch(Rectangle((x, y), w, h, fill=True, color='black', alpha=.5))
                    elif (j,i) in maze.int:
                        axs[k].add_patch(Rectangle((x, y), w, h, fill=True, color='blue', alpha=.3))
                        axs[k].text(x+tilesize/2, y+tilesize/2, maze.int[(j,i)])
                    elif (j,i) in maze.goal:
                        axs[k].add_patch(Rectangle((x, y), w, h, fill=True, color='yellow', alpha=.3))
                        axs[k].text(x+tilesize/2, y+tilesize/2, 'T')
                    elif i % 2 == j % 2:
                        axs[k].add_patch(Rectangle((x, y), w, h, fill=True, color='black', alpha=.1))
                        if (j,i) in maze.init:
                            axs[k].text(x+tilesize/2, y+tilesize/2, 'S')
                    elif maze.map[j,i]==' ':
                        axs[k].add_patch(Rectangle((x, y), w, h, fill=True, color='black', alpha=.2))
                        if (j,i) in maze.init:
                            axs[k].text(x+tilesize/2, y+tilesize/2, 'S')
            # grid lines
            for x in xs:
                axs[k].plot([x, x], [ys[0], ys[-1]], color='black', alpha=.33, linestyle=':')
            for y in ys:
                axs[k].plot([xs[0], xs[-1]], [y, y], color='black', alpha=.33, linestyle=':')

            angles = {'n': (180, 0), 's': (0,180), 'e': (270, 90), 'w': (90,270)}

            # plot the cuts
            for cut in cuts_info:
                cut_out = cut[0]
                cut_in = cut[1]
                if cut_out[-1] == q:
                    startxy = cut_out[0]
                    endxy = cut_in[0]
                    x_val = (startxy[1]+endxy[1])/2
                    z_val = (startxy[0]+endxy[0])/2
                    intensity = 1.0/2
                    radius = 0.1
                    if endxy[1] - startxy[1] == 1:
                        cut_dir = 'e'
                    elif startxy[1] - endxy[1] == 1:
                        cut_dir = 'w'
                    elif endxy[0] - startxy[0] == 1:
                        cut_dir = 's'
                    else:
                        cut_dir = 'n'
                    # axs[k].plot([y_val+ tilesize/2, y_val+ tilesize/2], [x_val+ tilesize/2, x_val+ tilesize/2], color='black', alpha=intensity, marker='o')
                    axs[k].add_patch(Wedge((x_val+ tilesize/2, z_val+ tilesize/2), radius, angles[cut_dir][0], angles[cut_dir][1], fill=True, color='black', alpha=intensity, ec="none"))

            axs[k].invert_yaxis()
            axs[k].axis('equal')
            axs[k].set_title("'{0}'".format(q))
    else:
        fig, axs = plt.subplots(1)
        fig.suptitle('Reactive Constraints')
        axs.set_title("'{0}'".format(qs[0]))

        for k,q in enumerate(qs):
            axs.xaxis.set_visible(False)
            axs.yaxis.set_visible(False)
            axs.set_xlim(xs[0], xs[-1])
            axs.set_ylim(ys[0], ys[-1])

            # draw the grid
            for i, x in enumerate(xs[:-1]):
                for j, y in enumerate(ys[:-1]):

                    if maze.map[j,i]=='*':
                        axs.add_patch(Rectangle((x, y), w, h, fill=True, color='black', alpha=.5))
                    elif (j,i) in maze.int:
                        axs.add_patch(Rectangle((x, y), w, h, fill=True, color='blue', alpha=.3))
                        axs.text(x+tilesize/2, y+tilesize/2, maze.int[(j,i)])
                    elif (j,i) in maze.goal:
                        axs.add_patch(Rectangle((x, y), w, h, fill=True, color='yellow', alpha=.3))
                        axs.text(x+tilesize/2, y+tilesize/2, 'T')
                    elif i % 2 == j % 2:
                        axs.add_patch(Rectangle((x, y), w, h, fill=True, color='black', alpha=.1))
                        if (j,i) in maze.init:
                            axs.text(x+tilesize/2, y+tilesize/2, 'S')
                    elif maze.map[j,i]==' ':
                        axs.add_patch(Rectangle((x, y), w, h, fill=True, color='black', alpha=.2))
                        if (j,i) in maze.init:
                            axs.text(x+tilesize/2, y+tilesize/2, 'S')
            # grid lines
            for x in xs:
                axs.plot([x, x], [ys[0], ys[-1]], color='black', alpha=.33, linestyle=':')
            for y in ys:
                axs.plot([xs[0], xs[-1]], [y, y], color='black', alpha=.33, linestyle=':')

            angles = {'n': (180, 0), 's': (0,180), 'e': (270, 90), 'w': (90,270)}

            # plot the cuts
            # st()
            for cut in cuts_info:
                cut_out = cut[0]
                cut_in = cut[1]
                if cut_out[-1] == q:
                    startxy = cut_out[0]
                    endxy = cut_in[0]
                    x_val = (startxy[1]+endxy[1])/2
                    z_val = (startxy[0]+endxy[0])/2
                    intensity = 1.0
                    radius = 0.1
                    if endxy[1] - startxy[1] == 1:
                        cut_dir = 'e'
                    elif startxy[1] - endxy[1] == 1:
                        cut_dir = 'w'
                    elif endxy[0] - startxy[0] == 1:
                        cut_dir = 's'
                    else:
                        cut_dir = 'n'
                    axs.add_patch(Wedge((x_val+ tilesize/2, z_val+ tilesize/2), radius, angles[cut_dir][0], angles[cut_dir][1], fill=True, color='black', alpha=intensity, ec="none"))

            axs.invert_yaxis()
            axs.axis('equal')
            axs.set_title("'{0}'".format(q))


    plt.show()
    fig.savefig("imgs/reactive_cuts.pdf")

def plot_solutions(maze, sols):
    npanels = len(sols)

    tilesize = 1
    xs = np.linspace(0, maze.len_x*tilesize, maze.len_x+1)
    ys = np.linspace(0, maze.len_y*tilesize, maze.len_y+1)

    fig, ax = plt.subplots(npanels)
    colorstr = 'red'

    if npanels == 1:
        # st()
        cuts = list(set(sols[0]))
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

        flow_value, flow_dict = nx.maximum_flow(G, maze.init[0], 'goal')


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
                    if (j,i) in maze.init:
                        ax.text(x+tilesize/2, y+tilesize/2, 'S')
                elif maze.map[j,i]==' ':
                    ax.add_patch(Rectangle((x, y), w, h, fill=True, color='black', alpha=.2))
                    if (j,i) in maze.init:
                        ax.text(x+tilesize/2, y+tilesize/2, 'S')
        # grid lines
        for x in xs:
            ax.plot([x, x], [ys[0], ys[-1]], color='black', alpha=.33, linestyle=':')
        for y in ys:
            ax.plot([xs[0], xs[-1]], [y, y], color='black', alpha=.33, linestyle=':')

        # draw cuts
        for cut in cuts:
            startxy = cut[0]
            endxy = cut[1]
            x_val = (startxy[0]+endxy[0])/2
            y_val = (startxy[1]+endxy[1])/2
            intensity = 1.0/2
            ax.plot([y_val+ tilesize/2, y_val+ tilesize/2], [x_val+ tilesize/2, x_val+ tilesize/2], color='black', alpha=intensity, marker='o')
            # ax.plot([xs[0], xs[-1]], [y, y], color='black', alpha=.33, linestyle=':')

        # draw flow
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

    else:

        for n in range(npanels):
            # st()
            cuts = list(set(sols[n]))
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

            flow_value, flow_dict = nx.maximum_flow(G, maze.init[0], 'goal')


            ax[n].xaxis.set_visible(False)
            ax[n].yaxis.set_visible(False)

            # grid "shades" (boxes)
            w, h = xs[1] - xs[0], ys[1] - ys[0]
            for i, x in enumerate(xs[:-1]):
                for j, y in enumerate(ys[:-1]):

                    if maze.map[j,i]=='*':
                        ax[n].add_patch(Rectangle((x, y), w, h, fill=True, color='black', alpha=.5))
                    elif (j,i) in maze.int:
                        ax[n].add_patch(Rectangle((x, y), w, h, fill=True, color='blue', alpha=.3))
                        ax[n].text(x+tilesize/2, y+tilesize/2, 'I')
                    elif (j,i) in maze.goal:
                        ax[n].add_patch(Rectangle((x, y), w, h, fill=True, color='yellow', alpha=.3))
                        ax[n].text(x+tilesize/2, y+tilesize/2, 'T')
                    elif i % 2 == j % 2:
                        ax[n].add_patch(Rectangle((x, y), w, h, fill=True, color='black', alpha=.1))
                        if (j,i) in maze.init:
                            ax[n].text(x+tilesize/2, y+tilesize/2, 'S')
                    elif maze.map[j,i]==' ':
                        ax[n].add_patch(Rectangle((x, y), w, h, fill=True, color='black', alpha=.2))
                        if (j,i) in maze.init:
                            ax[n].text(x+tilesize/2, y+tilesize/2, 'S')
            # grid lines
            for x in xs:
                ax[n].plot([x, x], [ys[0], ys[-1]], color='black', alpha=.33, linestyle=':')
            for y in ys:
                ax[n].plot([xs[0], xs[-1]], [y, y], color='black', alpha=.33, linestyle=':')

            # draw cuts
            for cut in cuts:
                startxy = cut[0]
                endxy = cut[1]
                x_val = (startxy[0]+endxy[0])/2
                y_val = (startxy[1]+endxy[1])/2
                intensity = 1.0/2
                ax[n].plot([y_val+ tilesize/2, y_val+ tilesize/2], [x_val+ tilesize/2, x_val+ tilesize/2], color='black', alpha=intensity, marker='o')
                # ax.plot([xs[0], xs[-1]], [y, y], color='black', alpha=.33, linestyle=':')

            # draw flow
            for out_node in flow_dict.keys():
                if out_node != 'goal':
                    startxy = out_node
                    for in_node in flow_dict[out_node]:
                        if in_node != 'goal':
                            endxy = in_node
                            intensity = flow_dict[out_node][in_node]/2
                            if intensity:
                                ax[n].plot([startxy[1]+ tilesize/2, endxy[1]+ tilesize/2], [startxy[0]+ tilesize/2, endxy[0]+ tilesize/2], color=colorstr, alpha=intensity, linestyle='-')

            ax[n].invert_yaxis()
            ax[n].axis('equal')
    plt.show()
    fig.savefig("imgs/mazes.pdf")
