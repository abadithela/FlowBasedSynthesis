'''
Generating test objective and the system objective and random grid layout
'''

import sys
sys.path.append('..')
import numpy as np
from ipdb import set_trace as st
import itertools


def generate_random_grid(gridsize, obstacle_coverage, props):
    '''
    Generate random grid depending on number of propositions.
    Assuming the system `goal' is not a proposition in the list.
    '''
    # get random S, I, T location
    nspecial_nodes = len(props) + 2 # One each for source and goal, and the intermediates.
    all_states = list(itertools.product(np.arange(0,gridsize), np.arange(0,gridsize)))
    number_of_states = len(all_states)
    obsnum = np.ceil(number_of_states * obstacle_coverage/100)
    choose = int(nspecial_nodes+obsnum)
    idx = np.random.choice(len(all_states),choose,replace=False)
    # set S,I,T locations
    init = [all_states[idx[0]]]
    goals = [all_states[idx[1]]]
    inter = [all_states[idx[k]] for k in range(2,nspecial_nodes)]
    # set the obstacles
    obs = [all_states[idx[nspecial_nodes+int(n)]] for n in np.arange(0,obsnum)]
    ints = {inter[k]: props[k] for k in range(len(props))}
    return init, ints, goals, obs

def generate_specs_and_propositions(type, num):
    '''
    Create system and test objective automatically
    '''
    props = []
    if type == 'reachability':
        sys_formula = 'F(goal)'
        test_formula = ''
        for k in range(num):
            props.append('I_'+str(k+1))
            test_formula += 'F(I_'+str(k+1)+') & '
        test_formula = test_formula[:-3]
    elif type == 'sequence':
        sys_formula = 'F(goal)'
        test_formula = ''
        for k in range(num):
            props.append('I_'+str(k+1))
            test_formula += 'F(I_'+str(k+1)+' & '
        test_formula = test_formula[:-3]
        for k in range(num):
            test_formula += ')'
    elif type == 'reaction':
        sys_formula = 'F(goal)'
        test_formula = ''
        for k in range(num):
            props.append('t_'+str(k+1))
            props.append('r_'+str(k+1))
            sys_formula += ' & G(t_'+str(k+1)+' -> F(r_'+str(k+1)+'))'
            test_formula += 'F(t_'+str(k+1)+') & '
        test_formula = test_formula[:-3]
    elif type == 'safety':
        sys_formula = 'F(goal)'
        test_formula = 'F(I)'
        props.append('I')
        for k in range(num):
            props.append('u_'+str(k+1))
            sys_formula += '& G(!(u_'+str(k+1)+'))'
    else:
        print('Not a valid task type.')

    return sys_formula, test_formula, props


if __name__ == "__main__":
    gridsize = 10
    obstacle_coverage = 0
    type = 'reaction'
    num = 3
    sys_formula, test_formula, props = generate_specs_and_propositions(type, num)
    init, ints, goals, obs = generate_random_grid(gridsize, obstacle_coverage, props)
    st()
