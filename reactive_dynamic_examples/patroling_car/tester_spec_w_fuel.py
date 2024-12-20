# Synthesizing a controller for the system
import sys
sys.path.append('..')
from ipdb import set_trace as st
from problem_data import *

# put the specs together
class Spec:
    def __init__(self,vars, init, safety, progress, env_vars, env_init, env_safety, env_progress):
        self.vars = vars
        self.init = init
        self.safety = safety
        self.progress = progress
        self.env_vars = env_vars
        self.env_init = env_init
        self.env_safety = env_safety
        self.env_progress = env_progress

# Tester specs
def get_tester_spec(init_pos, maze, GD, SD, cuts):
    z_str = 'Z_t' # Tester variables
    x_str = 'X_t' # Tester variables
    z = 'z' # System variables
    x = 'x'
    f = 'f'
    turn = 'turn'
    q = 'q'
    # tester guarantees
    vars = set_variables(maze, GD)
    init = set_init(init_pos, z_str, x_str, turn, q)
    safety = get_tester_safety(maze, z_str, x_str, z, x, f, turn, GD, SD, cuts, q)
    progress = get_tester_progress_empty(maze, cuts, z_str, x_str, q)
    # assumptions on the system
    env_vars = set_sys_variables(maze, GD)
    env_init = set_sys_init(z, x, f, q, maze)
    env_safety = get_system_safety(maze, GD, z, x,f, q, z_str, x_str, turn, cuts)
    env_progress = get_system_progress(maze, z, x)
    # create GR(1) spec
    tester_spec = Spec(vars, init, safety, progress, env_vars, env_init, env_safety, env_progress)

    return tester_spec

# Assumptions on the system
def set_sys_variables(maze, GD):
    vars = {}
    vars['x'] = (0,maze.len_x)
    vars['z'] = (0,maze.len_z)
    vars['f'] = (0,MAX_FUEL)
    qs = list(set([GD.node_dict[node][-1] for node in list(GD.nodes)]))
    vals = [str(q[1:]) for q in qs]
    vals = [int(val) for val in vals]
    vars['q'] = (int(min(vals)), int(max(vals)))
    return vars

def set_sys_init(z, x, f, q, maze):
    (z_p,x_p) = maze.init
    init = {x +' = '+str(x_p)+' && '+z+' = '+str(z_p) +' && '+ str(q)+"= 0 && "+f+" = "+ str(MAX_FUEL)}
    return init

# SYSTEM SAFETY
# turn based game
def turn_based_asm(z, x, turn, maze):
    turns = set()
    # system stays in place at turn = 1
    for x_p in range(0,maze.len_x):
        for z_p in range(0,maze.len_z):
            turns |= {'('+turn+' = 1 && '+z+' = '+str(z_p)+' && '+x+' = '+str(x_p)+') -> X('+z+' = '+str(z_p)+' && '+x+' = '+str(x_p)+')'}
    return turns

# change of q
def history_var_dynamics(GD, sys_z, sys_x, sys_f, q_str, maze):
    '''
    Determines how the history variable 'q' changes.
    '''

    hist_var_dyn = set()
    for node in list(GD.graph.nodes):
        out_node = GD.node_dict[node]
        out_state = out_node[0][0] # For the extra refueling
        out_fuel = out_node[0][1]
        out_q = out_node[-1]
        # st()
        current_state = '('+sys_z+' = '+str(out_state[0])+' && '+sys_x+' = '+str(out_state[1])+' && '+sys_f+' = '+str(out_fuel)+' && '+q_str+' = '+str(out_q[1:])+')'

        if out_state not in maze.goal: # not at goal
            next_state_str = current_state + ' || '
            edge_list = list(GD.graph.edges(node))
            for edge in edge_list:
                in_node = GD.node_dict[edge[1]] # TODO: For the extra refueling. Change fuel to just be a third element in tuple
                in_state = in_node[0][0]
                in_f = in_node[0][1]
                in_q = in_node[-1]
                next_state_str = next_state_str+'('+sys_z+' = '+str(in_state[0])+' && '+sys_x+' = '+str(in_state[1])+' && '+sys_f+' = '+str(in_f)+' && '+q_str+' = '+str(in_q[1:])+') || '

            next_state_str = next_state_str[:-4]
            hist_var_dyn |=  {current_state + ' -> X(' + next_state_str + ')'}
        else:
            hist_var_dyn |=  {current_state + ' -> X(' + current_state + ')'}
    return hist_var_dyn

def history_var_dynamics_merged(GD, sys_z, sys_x, q_str, maze, cuts):
    '''
    Determines how the history variable 'q' changes.
    similar to hist_var_dynamics but since we have refueling,
    we have
    '''
    transition_dict = dict()
    hist_var_dyn = set()
    for node in list(GD.graph.nodes):
        out_node = GD.node_dict[node]
        out_state = out_node[0][0] # For the extra refueling
        out_q = out_node[-1]
        current_state = '('+sys_z+' = '+str(out_state[0])+' && '+sys_x+' = '+str(out_state[1])+' && '+q_str+' = '+str(out_q[1:])+')'

        if current_state not in transition_dict.keys():
            transition_dict[current_state] = {current_state}

        if out_state not in maze.goal:
            edge_list = list(GD.graph.edges(node))
            # edge_list = [edge for edge in edge_list if edge not in cuts]
            for edge in edge_list:
                in_node = GD.node_dict[edge[1]] # TODO: For the extra refueling. Change fuel to just be a third element in tuple
                in_state = in_node[0][0]
                in_q = in_node[-1]
                next_state_str = '('+sys_z+' = '+str(in_state[0])+' && '+sys_x+' = '+str(in_state[1])+' && '+q_str+' = '+str(in_q[1:])+')'
                transition_dict[current_state] |= {next_state_str}

    for current_state, next_states in transition_dict.items():
        all_next_state_str = current_state
        for next_state in next_states:
            if next_state != current_state:
                all_next_state_str = all_next_state_str + ' || ' + next_state

        hist_var_dyn |=  {current_state + ' -> X(' + all_next_state_str + ')'}
    return hist_var_dyn

def get_system_safety(maze, GD, z, x, f, q, z_str, x_str, turn, cuts):
    safety = set()
    safety |= no_collision_asm(maze, z_str, x_str, z, x)
    safety |= history_var_dynamics(GD, z, x, f, q, maze)
    safety |= turn_based_asm(z, x, turn, maze)
    return safety

def get_system_progress(maze, z, x):
    progress = set()
    progress |= {'('+z+' = '+str(maze.goal[0][0])+' && '+x+' = '+str(maze.goal[0][1])+')'}
    return progress

# Tester guarantees
# VARS

def set_variables(maze, GD):
    vars = {}
    vars['X_t'] = (1,3) # manually changed to the tester reactive_area
    vars['Z_t'] = (-1,maze.len_z)
    vars['turn'] = (0,1)
    return vars

# initial conditions
def set_init(init_pos, z_str, x_str, turn, q_str):
    (z,x) = init_pos
    init = {x_str +' = '+str(x)+' && '+z_str+' = '+str(z)+' && '+turn+' = 1'}
    return init

# SAFETY
# no collision
def no_collision_asm(maze, z_str, x_str, z, x):
    static_positions = list(set([pos[0] for pos in STATIC_AREA]))
    no_collision_spec = set()
    for x_p in range(0,maze.len_x):
        for z_p in range(0,maze.len_z):
            if (z_p,x_p) not in static_positions:
                # no collision in same timestep
                no_collision_str = '((' + z_str + ' = '+str(z_p)+' && '+ x_str + ' = '+str(x_p) +') -> X !(' + z + ' = '+str(z_p)+' && '+ x + ' = '+str(x_p) +'))'
                no_collision_spec |= {no_collision_str}
    return no_collision_spec

def no_collision_grt(maze, z_str, x_str, z, x):
    static_positions = list(set([pos[0] for pos in STATIC_AREA]))
    no_collision_spec = set()
    for x_p in range(0,maze.len_x):
        for z_p in range(0,maze.len_z):
            if (z_p,x_p) not in static_positions:
                # no collision in same timestep
                no_collision_str = '((' + z + ' = '+str(z_p)+' && '+ x + ' = '+str(x_p) +') -> X !(' + z_str + ' = '+str(z_p)+' && '+ x_str + ' = '+str(x_p) +'))'
                no_collision_spec |= {no_collision_str}
    return no_collision_spec

# Dynamics
def restrictive_dynamics(z_str, x_str):
    test_dynamics_spec = {'(Z_t = 2) -> X((Z_t = 3) || (Z_t = 2) ||(Z_t = 1))'}
    test_dynamics_spec |= {'(Z_t = 1) -> X((Z_t = 1) || (Z_t = 2) ||(Z_t = 0))'}
    test_dynamics_spec |= {'(Z_t = 0) -> X((Z_t = -1) || (Z_t = 0) ||(Z_t = 1))'}
    test_dynamics_spec |= {'(Z_t = 3) -> X((Z_t = 2) || (Z_t = 3) ||(Z_t = 4))'}
    test_dynamics_spec |= {'(Z_t = 4) -> X((Z_t = 3) || (Z_t = 4) ||(Z_t = 5))'}
    test_dynamics_spec |= {'(Z_t = 5) -> X((Z_t = 4) || (Z_t = 5) ||(Z_t = -1))'}
    test_dynamics_spec |= {'(Z_t = -1) -> X(Z_t = -1)'}
    test_dynamics_spec |= {'(X_t = 2) -> X(X_t = 2)'}
    return test_dynamics_spec

# turn based game
def turn_based_grt(z_str, x_str, turn, maze):
    static_positions = list(set([pos[0] for pos in STATIC_AREA]))
    turns = set()
    # turn changes every step
    turns |= {'('+turn+' = 0 -> X('+turn+' = 1))'} # System turn to play
    turns |= {'('+turn+' = 1 -> X('+turn+' = 0))'} # Tester turn to play
    # testers stays in place at turn = 0
    for x_p in range(0,maze.len_x):
        for z_p in range(0,maze.len_z):
            if (z_p,x_p) not in static_positions:
                turns |= {'('+turn+' = 0 && '+z_str+' = '+str(z_p)+' && '+x_str+' = '+str(x_p)+') -> X('+z_str+' = '+str(z_p)+' && '+x_str+' = '+str(x_p)+')'}
    return turns

def occupy_cuts(GD, cuts, sys_z, sys_x, sys_f, test_z, test_x, q_str, turn):
    '''
    Tester needs to occupy the cells that correspond to the cuts.
    Tester needs to be in the cut state when the system is in a q position and it is the system's
    turn to act.
    '''
    cut_specs = set()
    for cut in cuts:
        out_node = cut[0]
        out_state = out_node[0][0]
        out_f = out_node[0][1]
        out_q = out_node[-1]
        in_node = cut[1]
        in_state = in_node[0][0]
        system_state = '('+ sys_z + ' = ' + str(out_state[0]) + ' && ' + sys_x + ' = ' + str(out_state[1]) + ' && '+sys_f+' = '+str(out_f)+' && '+q_str+' = '+str(out_q[1:])+' && '+turn+' = 0)'
        block_state = '('+ test_z + ' = ' + str(in_state[0]) + ' && ' + test_x + ' = ' + str(in_state[1])+')'
        cut_specs |= {system_state + ' -> ' + block_state}
    return cut_specs

def do_not_overconstrain(GD, cuts, sys_z, sys_x, sys_f, test_z, test_x, q_str, turn):
    '''
    Do not constrain edges that are not cut.
    '''
    cuts_without_in_q = [(cut[0],cut[1][0]) for cut in cuts]

    do_not_overconstrain = set()
    for node in list(GD.nodes):
        out_node = GD.node_dict[node]
        out_state = out_node[0][0]
        out_q = out_node[-1]
        out_fuel = out_node[0][1]
        current_state = '('+sys_z+' = '+str(out_state[0])+' && '+sys_x+' = '+str(out_state[1])+' && '+sys_f+' = '+str(out_fuel)+' && '+q_str+' = '+str(out_q[1:])+' && '+turn+' = 0)'
        state_str = ''
        edge_list = list(GD.graph.edges(node))
        for edge in edge_list:
            in_node = GD.node_dict[edge[1]]
            in_state = in_node[0][0]
            in_q = in_node[-1]
            in_fuel = in_node[0][1]

            if (out_node, (in_state, in_fuel)) not in cuts_without_in_q:
                if (in_state, in_fuel) not in STATIC_AREA:
                    state_str = state_str + '('+ test_z + ' = ' + str(in_state[0]) + ' && ' + test_x + ' = ' + str(in_state[1])+') || '

        if state_str != '':
            state_str = state_str[:-4]
            do_not_overconstrain |=  { current_state + ' -> !(' + state_str + ')'}
    return do_not_overconstrain

# Tester transiently blocks the system, but not forever
def transiently_block(z_str, x_str):
    '''
    If it is the tester turn, it should not choose to stay in the same
    blocking state in the next step
    '''
    transient_spec = set()
    transient_spec |= {'('+z_str+' = 6 && turn = 1) -> X(!('+z_str+' = 6))'}
    transient_spec |= {'('+z_str+' = 4 && turn = 1) -> X(!('+z_str+' = 4))'}
    transient_spec |= {'('+z_str+' = 2 && turn = 1) -> X(!('+z_str+' = 2))'}
    transient_spec |= {'('+z_str+' = 0 && turn = 1) -> X(!('+z_str+' = 0))'}
    return transient_spec

# Tester transiently blocks the system, but not forever
def transiently_block_states(z_str, x_str, states):
    '''
    z_str, x_str: variables for the tester string
    states: list of states that have to be transiently blocked.
    If it is the tester turn, it should not choose to stay in the same
    blocking state in the next step
    '''
    transient_spec = set()
    for (z,x) in states:
        transient_spec |= {'('+z_str+' = '+z+' && '+x_str+' = '+x+' && turn = 1) -> X(!('+z_str+' = '+z+' && '+x_str+' = '+x+'))'}
    return transient_spec

# full safety spec
def get_tester_safety(maze, z_str, x_str, z, x, f, turn, GD, SD, cuts, q):
    safety = set()
    safety |= no_collision_grt(maze, z_str, x_str, z, x)
    safety |= restrictive_dynamics(z_str, x_str)
    safety |= turn_based_grt(z_str, x_str, turn, maze)
    safety |= occupy_cuts(GD, cuts, z, x, f, z_str, x_str, q, turn)
    safety |= do_not_overconstrain(GD, cuts, z, x, f, z_str, x_str, q, turn)
    return safety

# TESTER PROGRESS
def get_tester_progress_empty(maze, cuts, test_z, test_x, q_str):
    progress = set()
    return progress
