import sys
sys.path.append('..')
import numpy as np
from ipdb import set_trace as st
import networkx as nx
import pdb
from cut_flow_fcns_bigm import solve_min
from inner_min import solve_inner_min
from construct_automata.main import get_virtual_product_graphs
from setup_graphs import GraphData
from find_bypass_flow import find_fby
from flow_constraints.plotting import highlight_cuts
from find_cuts import setup_nodes_and_edges
import time
import matplotlib.pyplot as plt

times = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: []}

mazefiles = {5: ["runtime_mazes/maze5.txt", "runtime_mazes/maze5b.txt", "runtime_mazes/maze5c.txt", "runtime_mazes/maze5d.txt"],
            1: ["runtime_mazes/maze1.txt", "runtime_mazes/maze1b.txt", "runtime_mazes/maze1c.txt", "runtime_mazes/maze1d.txt"],
            2: ["runtime_mazes/maze2.txt", "runtime_mazes/maze2b.txt", "runtime_mazes/maze2c.txt", "runtime_mazes/maze2d.txt"],
            3: ["runtime_mazes/maze3.txt", "runtime_mazes/maze3b.txt", "runtime_mazes/maze3c.txt", "runtime_mazes/maze3d.txt"],
            4: ["runtime_mazes/maze4.txt", "runtime_mazes/maze4b.txt", "runtime_mazes/maze4c.txt", "runtime_mazes/maze4d.txt"],
            0: ["runtime_mazes/maze0.txt"],
            6: ["runtime_mazes/maze6.txt", "runtime_mazes/maze6b.txt", "runtime_mazes/maze6c.txt", "runtime_mazes/maze6d.txt"]}

def make_runtime_plot():
    for num in mazefiles.keys():
        mazefilelist = mazefiles[num]
        for mazefile in mazefilelist:
            virtual, system, b_pi, virtual_sys = get_virtual_product_graphs(mazefile)
            GD, SD = setup_nodes_and_edges(virtual, virtual_sys, b_pi)
            ti = time.time()
            ftest, d, F = solve_min(GD, SD)
            cuts = [x for x in d.keys() if d[x] >= 0.9]
            fby = find_fby(GD, d)
            bypass_flow = sum([fby[j] for j in fby.keys() if j[1] in GD.sink])

            tf = time.time()
            del_t = tf - ti
            print("{0} obstacles was solved in {1} seconds".format(num, del_t))

            times[num].append(del_t)
        # st()

    keys = list(mazefiles.keys())
    keys.sort()

    mediantimes = [np.mean(times[num], axis=0) for num in keys]

    xs = []
    ys = []
    for obsnum in keys:
        for t in times[obsnum]:
            xs.append(obsnum)
            ys.append(t)

    fig, ax = plt.subplots()
    ax.plot(keys, mediantimes)
    ax.scatter(xs, ys, alpha = 0.5)

    ax.ticklabel_format(useOffset=False)
    ax.invert_xaxis()

    ax.set(xlabel='# Obstacles', ylabel='Runtime (s)',
           title='Runtime for 5x5 Maze')
    ax.grid()
    ax.set_facecolor('whitesmoke')
    plt.grid(True,linestyle='--')
    fig.savefig("runtimes.png")
    plt.show()

    st()


if __name__ == '__main__':
    make_runtime_plot()
