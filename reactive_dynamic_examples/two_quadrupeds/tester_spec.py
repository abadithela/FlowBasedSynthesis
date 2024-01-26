# Synthesizing a controller for the system
import sys
sys.path.append('..')
from pdb import set_trace as st

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
def get_tester_spec(init_pos, maze, GD, cuts):
    z_str = 'Z_t' # Tester variables
    x_str = 'X_t' # Tester variables
    z = 'z' # System variables
    x = 'x'
    turn = 'turn'
    q = 'q'
    vars = set_variables(maze, GD)
    init = set_init(init_pos, z_str, x_str, turn, q)
    safety = get_tester_safety(maze, z_str, x_str, z, x, turn, GD, cuts, q)
    progress = get_tester_progress_empty(maze, cuts, z_str, x_str, q)
    env_vars = set_sys_variables(maze, GD)
    env_init = set_sys_init(z, x, q, maze)
    env_safety = get_system_safety(maze, GD, z, x, q, z_str, x_str, turn)
    env_progress = get_system_progress(maze, z, x)

    tester_spec = Spec(vars, init, safety, progress, env_vars, env_init, env_safety, env_progress)

    return tester_spec

# Assumptions on the system
def set_sys_variables(maze, GD):
    vars = {}
    vars['x'] = (0,maze.len_x)
    vars['z'] = (0,maze.len_z)
    qs = list(set([GD.node_dict[node][-1] for node in list(GD.nodes)]))
    vals = [str(q[1:]) for q in qs]
    vals = [int(val) for val in vals]
    vars['q'] = (int(min(vals)), int(max(vals)))
    return vars

def set_sys_init(z, x, q, maze):
    (z_p,x_p) = maze.init
    init = {x +' = '+str(x_p)+' && '+z+' = '+str(z_p) +' && '+ str(q)+"= 0"}
    return init

# SYSTEM SAFETY
# turn based game
def turn_based_asm(z, x, turn, maze):
    turns = set()
    # system stays in place at turn = 1
    turns |= {'('+turn+'= 1 -> ('+z+' = X('+z+')&& '+x+' = X('+x+')))'}
    for x_p in range(0,maze.len_x):
        for z_p in range(0,maze.len_z):
            turns |= {'('+turn+' = 1 && '+z+' = '+str(z_p)+' && '+x+' = '+str(x_p)+') -> X('+z+' = '+str(z_p)+' && '+x+' = '+str(x_p)+')'}
    return turns

# change of q
def history_var_dynamics(GD, sys_z, sys_x, q_str, maze):
    '''
    Determines how the history variable 'q' changes.
    '''
    hist_var_dyn = set()
    for node in list(GD.graph.nodes):
        out_node = GD.node_dict[node]
        out_state = out_node[0]
        out_q = out_node[-1]
        current_state = '('+sys_z+' = '+str(out_state[0])+' && '+sys_x+' = '+str(out_state[1])+' && '+q_str+' = '+str(out_q[1:])+')'

        if out_state not in maze.goal: # not at goal
            next_state_str = ''
            edge_list = list(GD.graph.edges(node))
            for edge in edge_list:
                in_node = GD.node_dict[edge[1]]
                in_state = in_node[0]
                in_q = in_node[-1]
                next_state_str = next_state_str+'('+sys_z+' = '+str(in_state[0])+' && '+sys_x+' = '+str(in_state[1])+' && '+q_str+' = '+str(in_q[1:])+') || '

            next_state_str = next_state_str[:-4]
            hist_var_dyn |=  {current_state + ' -> X(' + next_state_str + ')'}
        else:
            hist_var_dyn |=  {current_state + ' -> X(' + current_state + ')'}
    return hist_var_dyn

def get_system_safety(maze, GD, z, x, q, z_str, x_str, turn):
    safety = set()
    safety |= no_collision_asm(maze, z_str, x_str, z, x)
    safety |= history_var_dynamics(GD, z, x, q, maze)
    safety |= turn_based_asm(z, x, turn, maze)
    return safety

def get_system_progress(maze, z, x):
    progress = set()
    # st()
    # for goal in maze.goal:
    progress |= {'('+z+' = '+str(maze.goal[0][0])+' && '+x+' = '+str(maze.goal[0][1])+')'}
    return progress

# Tester guarantees
# VARS

def set_variables(maze, GD):
    vars = {}
    vars['X_t'] = (0,maze.len_x)
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
    no_collision_spec = set()
    for x_p in range(0,maze.len_x):
        for z_p in range(0,maze.len_z):
            # no collision in same timestep
            no_collision_str = '!((' + z_str + ' = '+str(z_p)+' && '+ x_str + ' = '+str(x_p) +') && (' + z + ' = '+str(z_p)+' && '+ x + ' = '+str(x_p) +'))'
            no_collision_spec |= {no_collision_str}
    return no_collision_spec

def no_collision_grt(maze, z_str, x_str, z, x):
    no_collision_spec = set()
    for x_p in range(0,maze.len_x):
        for z_p in range(0,maze.len_z):
            # no collision in same timestep
            no_collision_str = '((' + z + ' = '+str(z_p)+' && '+ x + ' = '+str(x_p) +') -> X !(' + z_str + ' = '+str(z_p)+' && '+ x_str + ' = '+str(x_p) +'))'
            no_collision_spec |= {no_collision_str}
    return no_collision_spec

# dynamics
def restrictive_dynamics(z_str, x_str):
    dynamics_spec = set()
    dynamics_spec |= {'('+z_str+' = 6) -> X(('+z_str+' = 6) || ('+z_str+' = 5) || ('+z_str+' = -1))'}
    dynamics_spec |= {'('+z_str+' = 5) -> X(('+z_str+' = 6) || ('+z_str+' = 5) || ('+z_str+' = 4))'}
    dynamics_spec |= {'('+z_str+' = 4) -> X(('+z_str+' = 4) || ('+z_str+' = 3) || ('+z_str+' = 5))'}
    dynamics_spec |= {'('+z_str+' = 3) -> X(('+z_str+' = 4) || ('+z_str+' = 3) || ('+z_str+' = 2))'}
    dynamics_spec |= {'('+z_str+' = 2) -> X(('+z_str+' = 3) || ('+z_str+' = 2) || ('+z_str+' = 1))'}
    dynamics_spec |= {'('+z_str+' = 1) -> X(('+z_str+' = 2) || ('+z_str+' = 1) || ('+z_str+' = 0))'}
    dynamics_spec |= {'('+z_str+' = 0) -> X(('+z_str+' = 0) || ('+z_str+' = 1) || ('+z_str+' = -1))'}
    # Tester can exit to parking state -1 and must stay there
    dynamics_spec |= {'('+z_str+' = -1) -> X(('+z_str+' = -1))'}
    # Tester x variable is always 2
    dynamics_spec |= {'('+x_str+' = 2) -> X(('+x_str+' = 2))'}
    return dynamics_spec

# turn based game
def turn_based_grt(z_str, x_str, turn, maze):
    turns = set()
    # turn changes every step
    turns |= {'('+turn+' = 0 -> X('+turn+' = 1))'} # System turn to play
    turns |= {'('+turn+' = 1 -> X('+turn+' = 0))'} # Tester turn to play
    # testers stays in place at turn = 0
    for x_p in range(0,maze.len_x):
        for z_p in range(0,maze.len_z):
            turns |= {'('+turn+' = 0 && '+z_str+' = '+str(z_p)+' && '+x_str+' = '+str(x_p)+') -> X('+z_str+' = '+str(z_p)+' && '+x_str+' = '+str(x_p)+')'}
    return turns

def occupy_cuts(GD, cuts, sys_z, sys_x, test_z, test_x, q_str, turn):
    '''
    Tester needs to occupy the cells that correspond to the cuts.
    Tester needs to be in the cut state when the system is in a q position and it is the system's
    turn to act.
    '''
    cut_specs = set()
    for cut in cuts:
        out_node = cut[0]
        out_state = out_node[0]
        out_q = out_node[-1]
        in_node = cut[1]
        in_state = in_node[0]
        system_state = '('+ sys_z + ' = ' + str(out_state[0]) + ' && ' + sys_x + ' = ' + str(out_state[1]) + ' && ' +q_str+' = '+str(out_q[1:])+' && '+turn+' = 0)'
        block_state = '('+ test_z + ' = ' + str(in_state[0]) + ' && ' + test_x + ' = ' + str(in_state[1])+')'
        cut_specs |= {system_state + ' -> ' + block_state}
    return cut_specs

def do_not_overconstrain(GD, cuts, sys_z, sys_x, test_z, test_x, q_str, turn):
    '''
    Do not constrain edges that are not cut.
    '''
    do_not_overconstrain = set()
    for node in list(GD.nodes):
        out_node = GD.node_dict[node]
        out_state = out_node[0]
        out_q = out_node[-1]
        current_state = '('+sys_z+' = '+str(out_state[0])+' && '+sys_x+' = '+str(out_state[1])+' && '+q_str+' = '+str(out_q[1:])+' && '+turn+' = 0)'
        state_str = ''
        edge_list = list(GD.graph.edges(node))
        for edge in edge_list:
            # st()
            in_node = GD.node_dict[edge[1]]
            in_state = in_node[0]
            if (out_node,in_node) not in cuts:
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

# full safety spec
def get_tester_safety(maze, z_str, x_str, z, x, turn, GD, cuts, q):
    safety = set()
    safety |= no_collision_grt(maze, z_str, x_str, z, x)
    safety |= restrictive_dynamics(z_str, x_str)
    safety |= transiently_block(z_str, x_str)
    safety |= turn_based_grt(z_str, x_str, turn, maze)
    safety |= occupy_cuts(GD, cuts, z, x, z_str, x_str, q, turn)
    safety |= do_not_overconstrain(GD, cuts, z, x, z_str, x_str, q, turn)
    return safety

# TESTER PROGRESS
def get_tester_progress_empty(maze, cuts, test_z, test_x, q_str):
    progress = set()
    return progress
