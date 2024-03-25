'''
Solving a random grid layout with multiple intermediate nodes (I) in a sequence
using the MILP for static obstacles.
'''
import sys
sys.path.append('../..')
import numpy as np
import itertools

from static_examples.utils.solve_problem import solve_problem
from static_examples.utils.get_graphs import get_graphs
from static_examples.utils.setup_logger import logger
from ipdb import set_trace as st

FIXED = True

def find_cuts(number_intermediates, problem_data = []):
    obstacle_coverage = 0 # percentage of the grid that shall be covered by obstacles
    gridsize = 10
    mazefile = '10x10.txt'
    # for fixed locations
    if problem_data:
        init = problem_data['init']
        int_locs = problem_data['int_locs']
        goals = problem_data['goals']
        ints = {int_locs[k]: 'int_'+str(k+1) for k in range(len(int_locs))}
        obs = []
    else:
        # get random S, I, T location
        all_states = list(itertools.product(np.arange(0,gridsize), np.arange(0,gridsize)))
        number_of_states = len(all_states)
        obsnum = np.ceil(number_of_states * obstacle_coverage/100)
        choose = int(2 + number_intermediates + obsnum)
        idx = np.random.choice(len(all_states),choose,replace=False)

        init = [all_states[idx[0]]]
        goals = [all_states[idx[1]]]
        ints = {all_states[idx[k+2]]: 'int_'+str(k+1) for k in range(number_intermediates)}

        obs = [all_states[idx[2+number_intermediates+int(n)]] for n in np.arange(0,obsnum)]

    intstr = ''.join('%s = %s, ' % (val,key) for (key,val) in ints.items())
    print('Gridsize = '+str(gridsize)+': S = '+str(init)+', '+intstr+' T = '+str(goals))

    sys_formula = 'F(goal)'
    test_formula = ''
    for k in range(number_intermediates):
        test_formula += 'F(int_'+str(k+1)+' & '
    test_formula = test_formula[:-3]
    for k in range(number_intermediates):
        test_formula += ')'
    print(test_formula)


    virtual, system, b_pi, virtual_sys = get_graphs(sys_formula, test_formula, mazefile, init, ints, goals, obs, log)

    exit_status, annot_cuts, flow, bypass  = solve_problem(virtual, system, b_pi, virtual_sys, log, callback = False)
    print('exit status {0}'.format(exit_status))

    return annot_cuts


if __name__ == '__main__':
    number_intermediates = 4
    init = [(7, 2)]
    int_locs = [(5,2), (2, 1),(3, 4),(1, 8), (6,6), (8, 8)]
    goals = [(8, 3)]
    number_intermediates = len(int_locs)

    problem_data = {'init': init, 'int_locs': int_locs, 'goals': goals}
    find_cuts(number_intermediates, problem_data)
