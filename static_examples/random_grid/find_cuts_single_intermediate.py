'''
Solving a random grid layout with one intermediate node (I) using the MILP for static obstacles.
'''
import sys
sys.path.append('../..')
import numpy as np
import itertools

from static_examples.solve_problem import solve_problem
from static_examples.get_graphs import get_graphs

def find_cuts(gridsize):
    obstacle_coverage = 25 # percentage of the grid that shall be covered by obstacles
    mazefile = 'mazes/'+str(gridsize)+'x'+str(gridsize)+'.txt'

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
    print('S: {0}, I: {1}, T: {2}'.format(init, ints, goals))

    sys_formula = 'F(goal)'
    test_formula = 'F(int)'

    virtual, system, b_pi, virtual_sys = get_graphs(sys_formula, test_formula, mazefile, init, ints, goals, obs)

    exit_status, annot_cuts, flow, bypass = solve_problem(virtual, system, b_pi, virtual_sys)
    print('exit status {0}'.format(exit_status))

    return annot_cuts


if __name__ == '__main__':
    gridsize = 10
    find_cuts(gridsize)
