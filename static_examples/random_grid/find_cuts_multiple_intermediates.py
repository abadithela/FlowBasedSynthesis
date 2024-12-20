'''
Solving a random grid layout with multiple intermediate nodes (I) using the MILP for static obstacles.
'''
import sys
sys.path.append('../..')
import numpy as np
import itertools

from static_examples.solve_problem import solve_problem
from static_examples.get_graphs import get_graphs

def find_cuts(gridsize, number_intermediates):
    obstacle_coverage = 0 # percentage of the grid that shall be covered by obstacles
    mazefile = 'mazes/'+str(gridsize)+'x'+str(gridsize)+'.txt'

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
        test_formula += 'F(int_'+str(k+1)+') &'
    test_formula = test_formula[:-2]

    virtual, system, b_pi, virtual_sys = get_graphs(sys_formula, test_formula, mazefile, init, ints, goals, obs)

    exit_status, annot_cuts, flow, bypass = solve_problem(virtual, system, b_pi, virtual_sys)
    print('exit status {0}'.format(exit_status))

    return annot_cuts


if __name__ == '__main__':
    gridsize = 4
    number_intermediates = 2
    find_cuts(gridsize, number_intermediates)
