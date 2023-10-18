import sys
sys.path.append('..')
import numpy as np
from ipdb import set_trace as st
import networkx as nx
import pdb
from cut_flow_fcns_bigm import solve_min as solve_min_bigm
from cut_flow_fcns import solve_min
from cut_flow_fcns_bilevel import solve_bilevel
from inner_min import solve_inner_min
from construct_automata.main import get_virtual_product_graphs
from setup_graphs import GraphData
from find_bypass_flow import find_fby
from flow_constraints.plotting import highlight_cuts
from find_cuts import setup_nodes_and_edges
import time
import matplotlib.pyplot as plt

bigm_times = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: []}
min_times = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: []}
bilevel_times = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: []}

<<<<<<< HEAD
mazefiles = {5: ["runtime_mazes/maze5.txt"],# "runtime_mazes/maze5b.txt", "runtime_mazes/maze5c.txt", "runtime_mazes/maze5d.txt"],
            # 1: ["runtime_mazes/maze1.txt", "runtime_mazes/maze1b.txt", "runtime_mazes/maze1c.txt", "runtime_mazes/maze1d.txt"],
             2: ["runtime_mazes/maze2.txt"],# "runtime_mazes/maze2b.txt", "runtime_mazes/maze2c.txt", "runtime_mazes/maze2d.txt"],
             3: ["runtime_mazes/maze3.txt"],# "runtime_mazes/maze3b.txt", "runtime_mazes/maze3c.txt", "runtime_mazes/maze3d.txt"],
            4: ["runtime_mazes/maze4.txt"],# "runtime_mazes/maze4b.txt", "runtime_mazes/maze4c.txt", "runtime_mazes/maze4d.txt"],
            # 0: ["runtime_mazes/maze0.txt"],
            6: ["runtime_mazes/maze6.txt"]}# "runtime_mazes/maze6b.txt", "runtime_mazes/maze6c.txt", "runtime_mazes/maze6d.txt"]}
=======
# mazefiles = {5: ["runtime_mazes/maze5.txt", "runtime_mazes/maze5b.txt", "runtime_mazes/maze5c.txt", "runtime_mazes/maze5d.txt"],
#             1: ["runtime_mazes/maze1.txt", "runtime_mazes/maze1b.txt", "runtime_mazes/maze1c.txt", "runtime_mazes/maze1d.txt"],
#             2: ["runtime_mazes/maze2.txt", "runtime_mazes/maze2b.txt", "runtime_mazes/maze2c.txt", "runtime_mazes/maze2d.txt"],
#             3: ["runtime_mazes/maze3.txt", "runtime_mazes/maze3b.txt", "runtime_mazes/maze3c.txt", "runtime_mazes/maze3d.txt"],
#             4: ["runtime_mazes/maze4.txt", "runtime_mazes/maze4b.txt", "runtime_mazes/maze4c.txt", "runtime_mazes/maze4d.txt"],
#             0: ["runtime_mazes/maze0.txt"],
#             6: ["runtime_mazes/maze6.txt", "runtime_mazes/maze6b.txt", "runtime_mazes/maze6c.txt", "runtime_mazes/maze6d.txt"]}

mazefiles = {5: ["runtime_mazes/maze5.txt", "runtime_mazes/maze5b.txt", "runtime_mazes/maze5c.txt", "runtime_mazes/maze5d.txt"],
            0: ["runtime_mazes/maze0.txt"],
            2: ["runtime_mazes/maze2.txt", "runtime_mazes/maze2b.txt", "runtime_mazes/maze2c.txt", "runtime_mazes/maze2d.txt"],
            3: ["runtime_mazes/maze3.txt", "runtime_mazes/maze3b.txt", "runtime_mazes/maze3c.txt", "runtime_mazes/maze3d.txt"],
            4: ["runtime_mazes/maze4.txt", "runtime_mazes/maze4b.txt", "runtime_mazes/maze4c.txt", "runtime_mazes/maze4d.txt"],
            6: ["runtime_mazes/maze6.txt", "runtime_mazes/maze6b.txt", "runtime_mazes/maze6c.txt", "runtime_mazes/maze6d.txt"],
            1: ["runtime_mazes/maze1.txt", "runtime_mazes/maze1b.txt", "runtime_mazes/maze1c.txt", "runtime_mazes/maze1d.txt"]}
>>>>>>> dd7f0d353cfa54f778c820b559c8080cbe613976

def make_runtime_plot():
    for num in mazefiles.keys():
        mazefilelist = mazefiles[num]
        for mazefile in mazefilelist:
            virtual, system, b_pi, virtual_sys = get_virtual_product_graphs(mazefile)
            GD, SD = setup_nodes_and_edges(virtual, virtual_sys, b_pi)

            # solve using BigM
            print('--------- Solving using BigM ---------')
            ti = time.time()
            ftest, d, F = solve_min_bigm(GD, SD)
            tf = time.time()
            cuts = [x for x in d.keys() if d[x] >= 0.9]
            fby = find_fby(GD, d)
            bypass_flow = sum([fby[j] for j in fby.keys() if j[1] in GD.sink])
            del_t = tf - ti
            print("{0} obstacles was solved in {1} seconds using bigM - bypass flow {2}".format(num, del_t, bypass_flow))
            bigm_times[num].append(del_t)

<<<<<<< HEAD
            # solve using min
            # print('--------- Solving using Min ---------')
            # ti = time.time()
            # ftest, d, F = solve_min(GD, SD)
            # tf = time.time()
            # cuts = [x for x in d.keys() if d[x] >= 0.9]
            # fby = find_fby(GD, d)
            # bypass_flow = sum([fby[j] for j in fby.keys() if j[1] in GD.sink])
            # del_t = tf - ti
            # print("{0} obstacles was solved in {1} seconds using min - bypass flow {2}".format(num, del_t, bypass_flow))
            # min_times[num].append(del_t)
            if num in [4,5,6]:
                # solve using bilevel
                print('--------- Solving using bilevel ---------')
                ti = time.time()
                ftest, fby, d, F = solve_bilevel(GD, SD)
                tf = time.time()
                cuts = [x for x in d.keys() if d[x] >= 0.9]
                bypass_flow = sum([fby[j] for j in fby.keys() if j[1] in GD.sink])
                del_t = tf - ti
                print("{0} obstacles was solved in {1} seconds using bilevel - bypass flow {2}".format(num, del_t, bypass_flow))
                bilevel_times[num].append(del_t)
=======
            times[num].append(del_t)
            if num == 1:
                st()
>>>>>>> dd7f0d353cfa54f778c820b559c8080cbe613976

    keys = list(mazefiles.keys())
    keys.sort()

    # min_mediantimes = [np.mean(min_times[num], axis=0) for num in keys]
    bigm_mediantimes = [np.mean(bigm_times[num], axis=0) for num in keys]
    bilevel_mediantimes = [np.mean(bilevel_times[num], axis=0) for num in keys]

    xs_bigm = []
    ys_bigm = []
    xs_min = []
    ys_min = []
    xs_bilevel = []
    ys_bilevel = []
    for obsnum in keys:
        for t in bigm_times[obsnum]:
            xs_bigm.append(obsnum)
            ys_bigm.append(t)
        # for t in min_times[obsnum]:
        #     xs_min.append(obsnum)
        #     ys_min.append(t)
        for t in bilevel_times[obsnum]:
            xs_bilevel.append(obsnum)
            ys_bilevel.append(t)


    fig, ax = plt.subplots()
    ax.plot(keys, bigm_mediantimes, color = 'blue', label = 'bigM')
    # ax.plot(keys, min_mediantimes, color = 'green', label = 'min')
    ax.plot(keys, bilevel_mediantimes, color = 'red', label = 'bilevel')
    ax.scatter(xs_bigm, ys_bigm, alpha = 0.5, color = 'blue')
    # ax.scatter(xs_min, ys_min, alpha = 0.5, color = 'green')
    ax.scatter(xs_bilevel, ys_bilevel, alpha = 0.5, color = 'red')

    ax.ticklabel_format(useOffset=False)
    # ax.xticks(np.arange(0, 6, step=1))
    ax.invert_xaxis()

    ax.set(xlabel='# Obstacles', ylabel='Runtime (s)',
           title='Runtime for 5x5 Maze')
    ax.grid()
    ax.legend(loc="upper left")
    ax.set_facecolor('whitesmoke')
    plt.grid(True,linestyle='--')
    fig.savefig("runtimes.png")
    plt.show()

    st()


if __name__ == '__main__':
    make_runtime_plot()
