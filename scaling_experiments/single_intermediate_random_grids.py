'''
Solving empty grids of different sizes with one intermediate node using the MILP for static obstacles.
'''

import sys
sys.path.append('..')
import numpy as np
from ipdb import set_trace as st
import networkx as nx
import pdb
import time
import itertools
import matplotlib.pyplot as plt

from b_sys import get_B_sys
from b_product_1_intermed import get_B_product

from optimization.milp_static_obstacles import solve_min
from optimization.find_bypass_flow import find_fby
from optimization.milp_static_gurobipy import solve_max_gurobi

from components.transition_system import ProductTransys
from components.setup_graphs import GraphData, setup_nodes_and_edges
from components.plotting import plot_maze, plot_flow_on_maze, highlight_cuts
from components.tools import synchronous_product

plot_results = False
print_solution = False

def solve_instance(virtual, system, b_pi, virtual_sys):#, focus, cuts, presolve):
    GD, SD = setup_nodes_and_edges(virtual, virtual_sys, b_pi)

    ti = time.time()
    exit_status, ftest, d, flow = solve_max_gurobi(GD, SD)#, focus, cuts, presolve)
    tf = time.time()
    del_t = tf-ti

    fby = find_fby(GD, d)
    bypass_flow = sum([fby[j] for j in fby.keys() if j[1] in GD.sink])

    if print_solution:
        cuts = [x for x in d.keys() if d[x] >= 0.9]
        print('Cut {} edges in the virtual game graph.'.format(len(cuts)))
        print('The max flow through I is {}'.format(flow))
        print('The bypass flow is {}'.format(bypass_flow))
        for cut in cuts:
            print('Cutting {0} to {1}'.format(GD.node_dict[cut[0]], GD.node_dict[cut[1]]))

    if plot_results:
        cuts = [x for x in d.keys() if d[x] >= 0.9]
        highlight_cuts(cuts, GD, SD, virtual, virtual_sys)
        sys_cuts = [(GD.node_dict[cut[0]][0], GD.node_dict[cut[1]][0]) for cut in cuts]
        plot_flow_on_maze(system.maze, sys_cuts)

    return del_t, flow, bypass_flow

def plot_runtimes(runtimes):

    gridsizes = list(runtimes.keys())
    gridsizes.sort()

    meantimes = [np.mean(runtimes[num], axis=0) for num in gridsizes]

    xs = []
    ys = []
    for gridsize in gridsizes:
        for t in runtimes[gridsize]:
            xs.append(gridsize)
            ys.append(t)

    fig, ax = plt.subplots()
    ax.plot(gridsizes, meantimes, color = 'blue', label = 'MILP')
    ax.scatter(xs, ys, alpha = 0.5, color = 'blue')

    ax.ticklabel_format(useOffset=False)

    ax.set(xlabel='Grid Size N', ylabel='Runtime (s)',
           title='Runtime vs. NxN Grid')
    ax.grid()
    ax.legend(loc="upper left")
    ax.set_facecolor('whitesmoke')
    plt.grid(True,linestyle='--')
    fig.savefig("imgs/runtimes_1_int.pdf")
    plt.show()



if __name__ == '__main__':

    number_of_runs = 25
    obstacle_coverage = 15 # percentage of the grid that shall be covered by obstacles

    # mazefile = 'mazes/3x3.txt'

    mazefiles = {3: 'mazes/3x3.txt', 4: 'mazes/4x4.txt',5: 'mazes/5x5.txt',
                 6: 'mazes/6x6.txt', 7:'mazes/7x7.txt',
                8: 'mazes/8x8.txt', 9: 'mazes/9x9.txt', 10:'mazes/10x10.txt'}

    # mazefiles = {10:'mazes/10x10.txt'}


    runtimes = {}

    # foci = [0,1,2,3] # default is 0
    # cuts = [0,1,2,3] # default is -1 (whatever that may mean)
    # presolves = [-1,0,1,2]

    for gridsize in mazefiles.keys():
        del_ts = []
        mazefile = mazefiles[gridsize]

        for run in range(number_of_runs):
            # get random S, I, T location
            all_states = list(itertools.product(np.arange(0,gridsize), np.arange(0,gridsize)))
            number_of_states = len(all_states)
            obsnum = np.ceil(number_of_states * obstacle_coverage/100)
            choose = int(3+obsnum)
            idx = np.random.choice(len(all_states),choose,replace=False)
            # set S,I,T locations
            init = [all_states[idx[0]]]
            inter = all_states[idx[1]]
            goals = [all_states[idx[2]]]
            # set the obstacles
            obs = [all_states[idx[3+int(n)]] for n in np.arange(0,obsnum)]
            ints = {inter: 'int'}

            # get system
            system = ProductTransys()
            system.construct_sys(mazefile, init, ints, goals, obs)

            # get Buchi automata
            b_sys = get_B_sys(system.AP)
            b_pi = get_B_product()

            # get virtual sys
            virtual_sys = synchronous_product(system, b_sys)
            # get virtual product
            virtual = synchronous_product(system, b_pi)

            del_t, flow, bypass = solve_instance(virtual, system, b_pi, virtual_sys)#, focus, cuts, presolve)
            print("{0}: S = {1}, I = {2}, T = {3}".format(gridsize, init, ints, goals))
            print("Total time to solve opt: {1}, total flow = {2}, bypass = {3}".format(gridsize, del_t, flow, bypass))

            del_ts.append(del_t)

        runtimes.update({gridsize: del_ts})


    plot_runtimes(runtimes)
