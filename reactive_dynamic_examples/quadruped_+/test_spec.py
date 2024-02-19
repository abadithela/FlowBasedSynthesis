# Synthesizing a controller for the system
import sys
sys.path.append('..')
from pdb import set_trace as st
from test_progress import Tester_Progress_States

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

class Guarantees:
    def __init__(self, maze, GD, z_sys, x_sys, z_test, x_test, q, turn):
        self.maze = maze
        self.GD = GD
        self.z_sys = z_sys
        self.x_sys = x_sys
        self.z_test = z_test
        self.x_test = x_test
        self.q = q

class Assumptions:
    def __init__(self, maze, GD, z_sys, x_sys, z_test, x_test, q, turn):
        self.maze = maze
        self.GD = GD
        self.z_sys = z_sys
        self.x_sys = x_sys
        self.z_test = z_test
        self.x_test = x_test
        self.q = q
        self.turn = turn
        self.initialize()
    
    def initialize(self):
        self.set_sys_variables()
        self.set_sys_init()
        self.set_sys_safety()
        self.set_sys_progress()

    def set_sys_variables(self):
        self.vars = {}
        self.vars[self.x_sys] = (0,self.maze.len_x)
        self.vars[self.z_sys] = (0,self.maze.len_z)
        qs = list(set([self.GD.node_dict[node][-1] for node in list(self.GD.nodes)]))
        vals = [str(q[1:]) for q in qs]
        vals = [int(val) for val in vals]
        self.vars['q'] = (int(min(vals)), int(max(vals)))

    def set_sys_init(self):
        (z_p,x_p) = maze.init
        self.init = {self.x_sys +' = '+str(x_p)+' && '+self.z_sys+' = '+str(z_p) +' && '+ self.q+"= 0"}

    def set_sys_safety(self):
        self.safety = set()
        self.safety |= self.no_collision_asm()
        self.safety |= self.history_var_dynamics()
        self.safety |= self.turn_based_asm()

    def set_sys_progress(self):
        self.progress = set()
        self.progress |= {'('+self.z_sys+' = '+str(self.maze.goal[0][0])+' && '+self.x_sys+' = '+str(self.maze.goal[0][1])+')'}

    def no_collision_asm(self):
        no_collision_spec = set()
        for x_p in range(0,self.maze.len_x):
            for z_p in range(0,self.maze.len_z):
                no_collision_str = '!((' + self.z_test + ' = '+str(z_p)+' && '+ self.x_test + ' = '+str(x_p) +') && (' + self.z + ' = '+str(z_p)+' && '+ self.x + ' = '+str(x_p) +'))'
                no_collision_spec |= {no_collision_str}
        return no_collision_spec

    def history_var_dynamics(self):
        '''
        Determines how the history variable 'q' changes.
        '''
        hist_var_dyn = set()
        for node in list(self.GD.graph.nodes):
            out_node = self.GD.node_dict[node]
            out_state = out_node[0]
            out_q = out_node[-1]
            current_state = '('+self.z_sys+' = '+str(out_state[0])+' && '+self.x_sys+' = '+str(out_state[1])+' && '+self.q+' = '+str(out_q[1:])+')'

            if out_state not in self.maze.goal: # not at goal
                next_state_str = current_state + ' || '
                edge_list = list(self.GD.graph.edges(node))
                for edge in edge_list:
                    in_node = self.GD.node_dict[edge[1]]
                    in_state = in_node[0]
                    in_q = in_node[-1]
                    next_state_str = next_state_str+'('+self.z_sys+' = '+str(in_state[0])+' && '+self.x_sys+' = '+str(in_state[1])+' && '+self.q+' = '+str(in_q[1:])+') || '

                next_state_str = next_state_str[:-4]
                hist_var_dyn |=  {current_state + ' -> X(' + next_state_str + ')'}
            else:
                hist_var_dyn |=  {current_state + ' -> X(' + current_state + ')'}
        return hist_var_dyn

    def turn_based_asm(self):
        turns = set()
        # system stays in place at turn = 1
        turns |= {'('+self.turn+'= 1 -> ('+self.z_sys+' = X('+z+')&& '+self.x_sys+' = X('+x+')))'}
        for x_p in range(0,self.maze.len_x):
            for z_p in range(0,self.maze.len_z):
                turns |= {'('+self.turn+' = 1 && '+self.z_sys+' = '+str(z_p)+' && '+self.x_sys+' = '+str(x_p)+') -> X('+self.z_sys+' = '+str(z_p)+' && '+self.x_sys+' = '+str(x_p)+')'}
        return turns

    def get_sys_vars(self):
        return self.vars

    def get_sys_init(self):
        return self.init

    def get_sys_safety(self):
        return self.safety
    
    def get_sys_progress(self):
        return self.progress


class Guarantees:
    def __init__(self, maze, GD, z_sys, x_sys, z_test, x_test, q, turn, init_pos, cuts, z_test_park=False, x_test_park=False, static_area=[]):
        self.maze = maze
        self.GD = GD
        self.z_sys = z_sys
        self.x_sys = x_sys
        self.z_test = z_test
        self.x_test = x_test
        self.q = q
        self.turn = turn
        self.init_pos = init_pos
        self.cuts = cuts
        self.z_test_park = z_test_park # True/False. If True, the range of z_test is from (-1, maze.len_z)
        self.x_test_park = x_test_park
        self.static_area = static_area
        self.initialize()  

        self.get_blocked_states()

    def initialize(self):
        self.set_test_variables()
        self.set_test_init()
    
    def set_safety_and_progress(self):
        self.set_test_safety()
        self.set_test_progress()
    
    def get_blocked_states(self):
        pass
    
    def set_park_transitions(self):
        '''
        If either grid variable has a parking state for the tester, then this function is called
        to specify the cells from which the tester can exit to a parking state
        '''
        pass
    def set_test_vars(self):
        self.vars = {}
        if not self.x_test_park:
            self.vars[self.x_test] = (0, self.maze.len_x)
        else:
            self.vars[self.x_test] = self.x_test_park
        
        if not self.z_test_park:
            self.vars[self.z_test] = (0, self.maze.len_z)
        else:
            self.vars[self.z_test] = self.z_test_park
        
        self.vars['turn'] = (0,1)

    def set_test_init(self):
        (z,x) = self.init_pos.copy()
        self.init = {self.x_test +' = '+str(x)+' && '+self.z_test+' = '+str(z)+' && '+self.turn+' = 1'}

    def set_test_safety(self):
        self.safety = set()
        self.safety |= self.no_collision_grt()
        self.safety |= self.dynamics()
        self.safety |= self.turn_based_grt()
        self.safety |= self.occupy_cuts()
        self.safety |= self.do_not_overconstrain()
        self.safety |= self.transiently_block_states()
    
    def set_test_progress(self):
        self.progress = set()
    
    def no_collision_grt(self):
        no_collision_spec = set()
        for x_p in range(0, self.maze.len_x):
            for z_p in range(0, self.maze.len_z):
                # no collision in same timestep
                no_collision_str = '((' + self.z_sys + ' = '+str(z_p)+' && '+ self.x_sys + ' = '+str(x_p) +') -> X !(' + self.z_test + ' = '+str(z_p)+' && '+ self.x_test + ' = '+str(x_p) +'))'
                no_collision_spec |= {no_collision_str}
        return no_collision_spec

    def dynamics(self):
        # todo: Fix the dynamics specs here:
        # First take tester transitions on grid:
        dynamics = self.grid_transition_specs()
        dynamics |= self.parking_dynamics(dynamics)
        return dynamics
    
    
    def grid_transition_specs(self):
        '''
        Tester transitions on the maze except in static area.
        '''
        dynamics_spec = set()
        for ii in range(0,self.maze.len_z):
            for jj in range(0,self.maze.len_x):
                if (not self.maze.map[(ii,jj)] == '*') and ((ii,jj) not in self.static_area):
                    next_steps_string = '('+self.z_test+' = '+str(ii)+' && '+self.x_test+' = '+str(jj)+')'
                    for item in self.maze.next_state_dict[(ii,jj)]:
                        if item != (ii,jj) and item not in self.static_area:
                            next_steps_string = next_steps_string + ' || ('+self.z_test+' = '+str(item[0])+' && '+self.x_test+' = '+str(item[1])+')'
                    dynamics_spec |= {'('+self.z_test+' = '+str(ii)+' && '+self.x_test+' = '+str(jj)+') -> X(('+ next_steps_string +'))'}
        return dynamics_spec
    
    def parking_dynamics(self, dynamics):
        '''
        Tester transitions on the maze except in static area.
        '''
        parking_spec = set()
        if exist_z_park:
            z_park_st = [ii for ii in range(self.z_test_dom) if ii not in list(range(0,self.maze.len_z))]
            for jj in range(0,self.maze.len_x):
                if (not self.maze.map[(ii,jj)] == '*') and ((ii,jj) not in self.static_area):
                    next_steps_string = '('+self.z_test+' = '+str(ii)+' && '+self.x_test+' = '+str(jj)+')'
                    for item in self.maze.next_state_dict[(ii,jj)]:
                        if item != (ii,jj):
                            next_steps_string = next_steps_string + ' || ('+self.z_test+' = '+str(item[0])+' && '+self.x_test+' = '+str(item[1])+')'
                    dynamics_spec |= {'('+self.z_test+' = '+str(ii)+' && '+self.x_test+' = '+str(jj)+') -> X(('+ next_steps_string +'))'}
        return dynamics_spec
    
    def check_exist_park(self, domain):
        if domain is not None:
            if domain[0] == -1:
                return True
            else:
                return False
        
    def turn_based_grt(self):
        turns = set()
        # turn changes every step
        turns |= {'('+self.turn+' = 0 -> X('+self.turn+' = 1))'} # System turn to play
        turns |= {'('+self.turn+' = 1 -> X('+self.turn+' = 0))'} # Tester turn to play
        # testers stays in place at turn = 0
        for x_p in range(0,self.maze.len_x):
            for z_p in range(0,self.maze.len_z):
                turns |= {'('+self.turn+' = 0 && '+self.z_test+' = '+str(z_p)+' && '+self.x_test+' = '+str(x_p)+') -> X('+self.z_test+' = '+str(z_p)+' && '+self.x_test+' = '+str(x_p)+')'}
        return turns

    def occupy_cuts(self):
        pass
    
    def do_not_overconstrain(self):
        '''
        Do not constrain edges that are not cut.
        '''
        do_not_overconstrain = set()
        for node in list(self.GD.nodes):
            out_node = self.GD.node_dict[node]
            out_state = out_node[0]
            out_q = out_node[-1]
            current_state = '('+self.z_sys+' = '+str(out_state[0])+' && '+self.x_sys+' = '+str(out_state[1])+' && '+self.q+' = '+str(out_q[1:])+' && '+self.turn+' = 0)'
            state_str = ''
            edge_list = list(self.GD.graph.edges(node))
            for edge in edge_list:
                # st()
                in_node = self.GD.node_dict[edge[1]]
                in_state = in_node[0]
                if (out_node,in_node) not in self.cuts:
                    state_str = state_str + '('+ self.z_test + ' = ' + str(in_state[0]) + ' && ' + self.x_test + ' = ' + str(in_state[1])+') || '

            if state_str != '':
                state_str = state_str[:-4]
                do_not_overconstrain |=  { current_state + ' -> !(' + state_str + ')'}
        return do_not_overconstrain
    
    def transiently_block_states(self):
        '''
        z_test, x_test: variables for the tester string
        states: list of states that have to be transiently blocked.
        If it is the tester turn, it should not choose to stay in the same
        blocking state in the next step
        '''
        transient_spec = set()
        for (z,x) in self.transient_block_states:
            transient_spec |= {'('+self.z_test+' = '+z+' && '+self.x_test+' = '+x+' && turn = 1) -> X(!('+self.z_test+' = '+z+' && '+self.x_test+' = '+x+'))'}
        return transient_spec

    def get_test_vars(self):
        return self.vars

    def get_test_init(self):
        return self.init

    def get_test_safety(self):
        return self.safety
    
    def get_test_progress(self):
        return self.progress


# Tester specs
def get_tester_spec(init_pos, maze, GD, cuts):
    z_test = 'Z_t' # Tester variables
    x_test = 'X_t' # Tester variables
    z_sys = 'z' # System variables
    x_sys = 'x'
    turn = 'turn'
    q = 'q'
    
    guarantees_of_test = Guarantees(maze, GD, z_sys, x_sys, z_test, x_test, q, turn, init_pos, cuts)
    test_vars = set_variables(maze, GD)
    test_init = set_init(init_pos, z_test, x_test, turn, q)
    test_safety = get_tester_safety(maze, z_test, x_test, z_sys, x_sys, turn, GD, cuts, q)
    test_progress = get_tester_progress_empty(maze, cuts, z_test, x_test, q)

    assumptions_on_system = Assumptions(maze, GD, z_sys, x_sys, z_test, x_test, q)
    env_vars = assumptions_on_system.set_sys_variables()
    env_init = assumptions_on_system.set_sys_init()
    env_safety = get_system_safety(maze, GD, z_sys, x_sys, q, z_test, x_test, turn)
    env_progress = get_system_progress(maze, z_sys, x_sys)

    tester_spec = Spec(test_vars, test_init, test_safety, test_progress, env_vars, env_init, env_safety, env_progress)
    return tester_spec

# Dynamics
def restrictive_dynamics(z_test, x_test):
    dynamics_spec = set()
    dynamics_spec |= {'('+z_test+' = 6) -> X(('+z_test+' = 6) || ('+z_test+' = 5) || ('+z_test+' = -1))'}
    dynamics_spec |= {'('+z_test+' = 5) -> X(('+z_test+' = 6) || ('+z_test+' = 5) || ('+z_test+' = 4))'}
    dynamics_spec |= {'('+z_test+' = 4) -> X(('+z_test+' = 4) || ('+z_test+' = 3) || ('+z_test+' = 5))'}
    dynamics_spec |= {'('+z_test+' = 3) -> X(('+z_test+' = 4) || ('+z_test+' = 3) || ('+z_test+' = 2))'}
    dynamics_spec |= {'('+z_test+' = 2) -> X(('+z_test+' = 3) || ('+z_test+' = 2) || ('+z_test+' = 1))'}
    dynamics_spec |= {'('+z_test+' = 1) -> X(('+z_test+' = 2) || ('+z_test+' = 1) || ('+z_test+' = 0))'}
    dynamics_spec |= {'('+z_test+' = 0) -> X(('+z_test+' = 0) || ('+z_test+' = 1) || ('+z_test+' = -1))'}
    dynamics_spec |= {'('+z_test+' = -1) -> X(('+z_test+' = -1))'}
    dynamics_spec |= {'('+x_test+' = 2) -> X(('+x_test+' = 2))'}
    return dynamics_spec

# turn based game
def turn_based_grt(z_test, x_test, turn, maze):
    turns = set()
    # turn changes every step
    turns |= {'('+turn+' = 0 -> X('+turn+' = 1))'} # System turn to play
    turns |= {'('+turn+' = 1 -> X('+turn+' = 0))'} # Tester turn to play
    # testers stays in place at turn = 0
    for x_p in range(0,maze.len_x):
        for z_p in range(0,maze.len_z):
            turns |= {'('+turn+' = 0 && '+z_test+' = '+str(z_p)+' && '+x_test+' = '+str(x_p)+') -> X('+z_test+' = '+str(z_p)+' && '+x_test+' = '+str(x_p)+')'}
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

# Tester transiently blocks the system, but not forever
def transiently_block(z_test, x_test):
    '''
    If it is the tester turn, it should not choose to stay in the same
    blocking state in the next step
    '''
    transient_spec = set()
    transient_spec |= {'('+z_test+' = 6 && turn = 1) -> X(!('+z_test+' = 6))'}
    transient_spec |= {'('+z_test+' = 4 && turn = 1) -> X(!('+z_test+' = 4))'}
    transient_spec |= {'('+z_test+' = 2 && turn = 1) -> X(!('+z_test+' = 2))'}
    transient_spec |= {'('+z_test+' = 0 && turn = 1) -> X(!('+z_test+' = 0))'}
    return transient_spec

# Tester transiently blocks the system, but not forever
def transiently_block_states(z_test, x_test, states):
    '''
    z_test, x_test: variables for the tester string
    states: list of states that have to be transiently blocked.
    If it is the tester turn, it should not choose to stay in the same
    blocking state in the next step
    '''
    transient_spec = set()
    for (z,x) in states:
        transient_spec |= {'('+z_test+' = '+z+' && '+x_test+' = '+x+' && turn = 1) -> X(!('+z_test+' = '+z+' && '+x_test+' = '+x+'))'}
    return transient_spec

# full safety spec
def get_tester_safety(maze, z_test, x_test, z, x, turn, GD, cuts, q):
    safety = set()
    safety |= no_collision_grt(maze, z_test, x_test, z, x)
    safety |= restrictive_dynamics(z_test, x_test)
    safety |= turn_based_grt(z_test, x_test, turn, maze)
    safety |= occupy_cuts(GD, cuts, z, x, z_test, x_test, q, turn)
    safety |= do_not_overconstrain(GD, cuts, z, x, z_test, x_test, q, turn)

    safety |= transiently_block(z_test, x_test)
    # progress_states = Tester_Progress_States()
    # states = progress_states.compute_tester_nodes()
    # transiently_block_states(z_test, x_test, states)
    return safety