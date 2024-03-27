import sys
sys.path.append('../..')
import os
import time
import networkx as nx
from ipdb import set_trace as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Wedge
import datetime


def highlight_history_cuts(cuts, GD, SD, virtual, virtual_sys):
    '''
    Save an image of the graphs with the cuts highlighted for each history variable
    Make sure that the product graphs are called from flow_constraints/products.
    '''
    annot_cuts = [(GD.node_dict[cut[0]], GD.node_dict[cut[1]]) for cut in cuts]
    sys_cuts = [(GD.node_dict[cut[0]][0], GD.node_dict[cut[1]][0]) for cut in cuts]
    sys_cuts_annot = [((cut[0], q1), (cut[1], q2)) for cut in sys_cuts for q1 in virtual_sys.AP for q2 in virtual_sys.AP]

    virtual.plot_with_highlighted_edges(annot_cuts, "imgs/virtual_with_cuts")

    srcs = {'q0': (1,0), 'q6': (0,0), 'q7': (1,2)}
    # st()

    reactive_cuts = dict()
    for q in virtual.AP:
        reactive_cuts[q] = []

    for cut in annot_cuts:
        q = cut[0][1]
        reactive_cuts[q].append((cut[0][0], cut[1][0]))

    for q, reactive_cuts_at_q in reactive_cuts.items():
        if not reactive_cuts[q] == []:
            sys_cuts_annot = [((cut[0], q1), (cut[1], q2)) for cut in reactive_cuts_at_q for q1 in virtual_sys.AP for q2 in virtual_sys.AP]
            virtual_sys.plot_with_highlighted_edges_and_node(sys_cuts_annot, f"imgs/virtual_sys_with_cuts_{q}", (srcs[q],'q1'))

    st()

def make_history_plots(cuts, GD, maze):
    plt.rcParams.update({"text.usetex": True,"font.family": "Helvetica"})

    try:
        if isinstance(cuts[0][0][-1], str):
            cuts_info = cuts
        else:
            cuts_info = [(GD.node_dict[i], GD.node_dict[j]) for (i,j) in cuts]
    except:
        cuts_info = [(GD.node_dict[i], GD.node_dict[j]) for (i,j) in cuts]
    #
    # qs = list(set([item[0][-1] for item in cuts_info]))

    # cuts_info = [(GD.node_dict[i], GD.node_dict[j]) for (i,j) in cuts]

    qs = list(set([item[0][-1] for item in cuts]))
    reactive_cuts = dict()
    for q in qs:
        reactive_cuts[q] = [item for item in cuts if item[0][-1]==q]

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
                        axs[k].add_patch(Rectangle((x, y), w, h, fill=True, color='#648fff', alpha=.3))
                        axs[k].text(x+tilesize*0.45, y+tilesize*0.65, r'$'+str(maze.int[(j,i)])+'$', fontsize = 25)
                    elif (j,i) in maze.goal:
                        axs[k].add_patch(Rectangle((x, y), w, h, fill=True, color='#ffb000', alpha=.3))
                        axs[k].text(x+tilesize*0.4, y+tilesize*0.65, r'$T$', fontsize = 25)
                    elif (j,i) in maze.init:
                        axs[k].text(x+tilesize*0.4, y+tilesize*0.65, r'$S$', fontsize = 25)
                    elif maze.map[j,i]==' ':
                        axs[k].add_patch(Rectangle((x, y), w, h, fill=True, color='#ffffff', alpha=.2))

            # grid lines
            for x in xs:
                axs[k].plot([x, x], [ys[0], ys[-1]], color='black', alpha=.33)
            for y in ys:
                axs[k].plot([xs[0], xs[-1]], [y, y], color='black', alpha=.33)

            angles = {'n': (180, 0), 's': (0,180), 'e': (270, 90), 'w': (90,270)}

            # plot the cuts
            width = tilesize/20
            for cut in reactive_cuts[q]:
                startxy = cut[0][0]
                endxy = cut[1][0]
                delx = startxy[0] - endxy[0]
                dely = startxy[1] - endxy[1]
                if delx == 0:
                    if dely < 0:
                        axs[k].add_patch(Rectangle((startxy[1]- width/2 - dely*tilesize , startxy[0] - width/2), width, tilesize+width, fill=True, color='black', alpha=1.0))
                    else:
                        axs[k].add_patch(Rectangle((startxy[1]- width/2 , startxy[0]- width/2), width, tilesize+width, fill=True, color='black', alpha=1.0))
                elif dely == 0:
                    if delx < 0:
                        axs[k].add_patch(Rectangle((startxy[1]- width/2, startxy[0]- width/2 - delx*tilesize), tilesize+width, width, fill=True, color='black', alpha=1.0))
                    else:
                        axs[k].add_patch(Rectangle((startxy[1]- width/2, startxy[0]- width/2), tilesize + width, width, fill=True, color='black', alpha=1.0))

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
            width = tilesize/20
            for cut in reactive_cuts[q]:
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

            axs.invert_yaxis()
            axs.axis('equal')
            axs.set_title("'{0}'".format(q))


    plt.show()
    now =  str(datetime.datetime.now())
    fig.savefig("imgs/reactive_cuts"+now+".pdf")
