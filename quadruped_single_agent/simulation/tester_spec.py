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
def get_tester_spec(init_pos, maze):
    z_str = 'env_z'
    x_str = 'env_x'
    z = 'z'
    x = 'x'
    turn = 'turn'
    vars = set_variables(maze)
    init = set_init(init_pos, z_str, x_str, turn)
    safety = get_tester_safety(maze, z_str, x_str, z, x, turn)
    progress = get_tester_progress(maze, z_str, x_str)
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
def turn_based_asm(z, x, turn):
    turns = set()
    # system stays in place at turn = 1
    turns |= {'('+turn+'= 1 && '+z+' = X('+z+')&& '+x+' = X('+x+'))'}
    return turns

def get_system_safety(maze, z, x, z_str, x_str, turn):
    safety = set()
    safety |=  no_collision(maze, z_str, x_str, z, x)
    safety |= maze.transition_specs(z, x)
    # safety |= turn_based_asm(z, x, turn)
    return safety

def get_system_progress(maze, z, x):
    progress = set()
    progress |= {'('+z+' = '+str(maze.goal[0])+' && '+x+' = '+str(maze.goal[1])+')'}
    return progress

# Tester guarantees
# VARS
def set_variables(maze):
    vars = {}
    vars['env_x'] = (0,maze.len_x)
    vars['env_z'] = (0,maze.len_z)
    vars['turn'] = (0,1)
    return vars

# initial conditions
def set_init(init_pos, z_str, x_str, turn):
    (z,x) = init_pos
    init = {x_str +' = '+str(x)+' && '+z_str+' = '+str(z)+' && '+turn+' = 0'}
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
    return no_collision_spec

# dynamics
def restrictive_dynamics(z_str, x_str):
    dynamics_spec = {'('+z_str+'= 4) -> X(('+z_str+' = 4) ||('+z_str+' = 3))'}
    dynamics_spec |= {'('+z_str+' = 3) -> X(('+z_str+' = 4) || ('+z_str+' = 3) ||('+z_str+' = 2))'}
    dynamics_spec |= {'('+z_str+' = 2) -> X(('+z_str+' = 3) || ('+z_str+' = 2) ||('+z_str+' = 1))'}
    dynamics_spec |= {'('+z_str+' = 1) -> X(('+z_str+' = 2) || ('+z_str+' = 1))'}
    dynamics_spec |= {'('+x_str+' = 2) -> X(('+x_str+' = 2))'}
    return dynamics_spec

# turn based game
def turn_based_grt(z_str, x_str, turn):
    turns = set()
    # turn changes every step
    turns |= {'('+turn+' = 0 -> X('+turn+' = 1))'}
    turns |= {'('+turn+' = 1 -> X('+turn+' = 0))'}
    # testers stays in place at turn = 0
    # turns |= {'('+turn+' = 0 && '+z_str+' = X('+z_str+') && '+x_str+' = X('+x_str+'))'}
    # turn changes
    # turns |= {'!('+turn+'= X('+turn+'))'}
    return turns

# full safety spec
def get_tester_safety(maze, z_str, x_str, z, x, turn):
    safety = set()
    safety |= no_collision(maze, z_str, x_str, z, x)
    safety |= restrictive_dynamics(z_str, x_str)
    safety |= turn_based_grt(z_str, x_str, turn)
    return safety

# PROGRESS
def get_tester_progress(maze, z_str, x_str):
    progress = set()
    progress |= {'('+x_str+' = 2 && '+z_str+' = 1) || ('+x_str+' = 2 && '+z_str+' = 3)'}
    return progress
