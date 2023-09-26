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
    z_str = 'env_z'
    x_str = 'env_x'
    z = 'z'
    x = 'x'
    turn = 'turn'
    q = 'q'
    vars = set_variables(maze, GD)
    init = set_init(init_pos, z_str, x_str, turn, q)
    safety = get_tester_safety(maze, z_str, x_str, z, x, turn, GD, cuts, q)
    progress = get_tester_progress(maze, z_str, x_str, q)
    env_vars = set_sys_variables(maze)
    env_init = set_sys_init(z, x, maze)
    env_safety = get_system_safety(maze, z, x, z_str, x_str, turn)
    env_progress = get_system_progress(maze, z, x)

    tester_spec = Spec(vars, init, safety, progress, env_vars, env_init, env_safety, env_progress)

    return tester_spec

# Assumptions on the system
def set_sys_variables(maze):
    vars = {}
    vars['x'] = (0,maze.len_x)
    vars['z'] = (0,maze.len_z)
    return vars

def set_sys_init(z, x, maze):
    (z_p,x_p) = maze.init
    init = {x +' = '+str(x_p)+' && '+z+' = '+str(z_p)}
    return init

# turn based game
def turn_based_asm(z, x, turn, maze):
    turns = set()
    # system stays in place at turn = 1
    turns |= {'('+turn+'= 1 -> ('+z+' = X('+z+')&& '+x+' = X('+x+')))'}
    for x_p in range(0,maze.len_x):
        for z_p in range(0,maze.len_z):
            turns |= {'('+turn+' = 1 && '+z+' = '+str(z_p)+' && '+x+' = '+str(x_p)+') -> X('+z+' = '+str(z_p)+' && '+x+' = '+str(x_p)+')'}
    return turns

def get_system_safety(maze, z, x, z_str, x_str, turn):
    safety = set()
    safety |= no_collision(maze, z_str, x_str, z, x)
    safety |= maze.transition_specs(z, x)
    safety |= turn_based_asm(z, x, turn, maze)
    return safety

def get_system_progress(maze, z, x):
    progress = set()
    progress |= {'('+z+' = '+str(maze.goal[0])+' && '+x+' = '+str(maze.goal[1])+')'}
    return progress

# Tester guarantees
# VARS

def set_variables(maze, GD):
    vars = {}
    vars['env_x'] = (0,maze.len_x)
    vars['env_z'] = (0,maze.len_z)
    vars['turn'] = (0,1)
    qs = list(set([GD.node_dict[node][-1] for node in list(GD.nodes)]))
    vals = [str(q[1:]) for q in qs]
    vars['q'] = (int(min(vals)), int(max(vals)))
    return vars

# initial conditions
def set_init(init_pos, z_str, x_str, turn, q_str):
    (z,x) = init_pos
    init = {x_str +' = '+str(x)+' && '+z_str+' = '+str(z)+' && '+turn+' = 0 && '+q_str+' = 0'}
    return init

# SAFETY
# no collision
def no_collision(maze, z_str, x_str, z, x):
    no_collision_spec = set()
    for x_p in range(0,maze.len_x):
        for z_p in range(0,maze.len_z):
            # no collision in same timestep
            no_collision_str = '!((' + z_str + ' = '+str(z_p)+' && '+ x_str + ' = '+str(x_p) +') && (' + z + ' = '+str(z_p)+' && '+ x + ' = '+str(x_p) +'))'
            no_collision_spec |= {no_collision_str}
    # st()
    return no_collision_spec

# dynamics
def restrictive_dynamics(z_str, x_str):
    dynamics_spec = {'('+z_str+' = 4) -> X(('+z_str+' = 4) || ('+z_str+' = 3))'}
    dynamics_spec |= {'('+z_str+' = 3) -> X(('+z_str+' = 4) || ('+z_str+' = 3) ||('+z_str+' = 2))'}
    dynamics_spec |= {'('+z_str+' = 2) -> X(('+z_str+' = 3) || ('+z_str+' = 2) ||('+z_str+' = 1))'}
    dynamics_spec |= {'('+z_str+' = 1) -> X(('+z_str+' = 2) || ('+z_str+' = 1))'}
    dynamics_spec |= {'('+x_str+' = 2) -> X(('+x_str+' = 2))'}
    return dynamics_spec

# turn based game
def turn_based_grt(z_str, x_str, turn, maze):
    turns = set()
    # turn changes every step
    turns |= {'('+turn+' = 0 -> X('+turn+' = 1))'}
    turns |= {'('+turn+' = 1 -> X('+turn+' = 0))'}
    # testers stays in place at turn = 0
    for x_p in range(0,maze.len_x):
        for z_p in range(0,maze.len_z):
            turns |= {'('+turn+' = 0 && '+z_str+' = '+str(z_p)+' && '+x_str+' = '+str(x_p)+') -> X('+z_str+' = '+str(z_p)+' && '+x_str+' = '+str(x_p)+')'}
    return turns

# change of q
def history_var_dynamics(GD, sys_z, sys_x, q_str):
    '''
    Determines how the history variable 'q' changes.
    '''
    hist_var_dyn = set()
    for node in list(GD.graph.nodes):
        out_node = GD.node_dict[node]
        out_state = out_node[0]
        out_q = out_node[-1]
        current_state = '('+sys_z+' = '+str(out_state[0])+' && '+sys_x+' = '+str(out_state[1])+' && '+q_str+' = '+str(out_q[1:])+')'

        if out_state != (0,4): # not at goal
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

def occupy_cuts(GD, cuts, sys_z, sys_x, test_z, test_x, q_str, turn):
    '''
    Tester needs to occupy the cells that correspond to the cuts.
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
    # st()
    return cut_specs

def do_not_excessively_constrain(GD, cuts, sys_z, sys_x, test_z, test_x, q_str, turn):
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
    # st()
    return do_not_overconstrain

# full safety spec
def get_tester_safety(maze, z_str, x_str, z, x, turn, GD, cuts, q):
    safety = set()
    safety |= no_collision(maze, z_str, x_str, z, x)
    safety |= restrictive_dynamics(z_str, x_str)
    safety |= turn_based_grt(z_str, x_str, turn, maze)
    safety |= history_var_dynamics(GD, z, x, q)
    safety |= occupy_cuts(GD, cuts, z, x, z_str, x_str, q, turn)
    safety |= do_not_excessively_constrain(GD, cuts, z, x, z_str, x_str, q, turn)
    return safety

# TESTER PROGRESS
def get_tester_progress(maze, z_str, x_str, q_str):
    progress = set()
    # progress |= {'('+q_str+' = 2 || '+q_str+' = 6)'}
    # progress |= {'('+z_str+' = 3 && '+x_str+' = 2) || ('+z_str+' = 1 && '+x_str+' = 2)'}

    return progress
