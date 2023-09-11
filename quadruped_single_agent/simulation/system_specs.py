" Script containing specifications for the system and tester"
import sys
sys.path.append('..')
from maze_network import MazeNetwork
from pdb import set_trace as st

# Class env_specs corresponds to a general environment that the system can handle.
class env_specs:
    def __init__(self, maze, sys_zstr, sys_xstr):
        self.maze = maze
        self.vars = {}
        self.init = set()
        self.safety = set()
        self.progress = set()
        self.zstr = 'env_z'
        self.xstr = 'env_x'
        self.sys_zstr = sys_zstr
        self.sys_xstr = sys_xstr
    
    def variables(self):
        # State indicated by: (z,x)
        self.vars[self.zstr] = (0, self.maze.len_z)
        self.vars[self.xstr] = (0, self.maze.len_x)
    
    def set_init(self, env_init):
        self.zinit, self.xinit = env_init
        init_string = self.zstr + ' = ' + str(self.zinit) + ' & ' + self.xstr + ' = ' + str(self.xinit)
        self.init |= {init_string}
    
    def no_collide(self):
        no_collide_spec = set()
        for x in range(0,self.maze.len_x):
            for z in range(0,self.maze.len_z):
                no_collide_str = '!((' + self.sys_zstr + ' = '+str(z)+' && '+ self.sys_xstr + ' = '+str(x) +') && (' + self.zstr + ' = '+str(z)+' && '+ self.xstr + ' = '+str(x) +'))'
                no_collide_spec |= {no_collide_str}
        return no_collide_spec

    def restrictive_dynamics(self):
        dynamics_spec = {'('+self.zstr+'= 4) -> X(('+self.zstr+' = 4) ||('+self.zstr+' = 3))'}
        dynamics_spec |= {'('+self.zstr+' = 3) -> X(('+self.zstr+' = 4) || ('+self.zstr+' = 3) ||('+self.zstr+' = 2))'}
        dynamics_spec |= {'('+self.zstr+' = 2) -> X(('+self.zstr+' = 3) || ('+self.zstr+' = 2) ||('+self.zstr+' = 1))'}
        dynamics_spec |= {'('+self.zstr+' = 1) -> X(('+self.zstr+' = 2) || ('+self.zstr+' = 1))'}
        dynamics_spec |= {'('+self.xstr+' = 2) -> X(('+self.xstr+' = 2))'}
        return dynamics_spec

    def set_safety(self):
        dynamics = self.maze.transition_specs(self.zstr, self.xstr)
        #dynamics = self.restrictive_dynamics()
        no_collide = self.no_collide()
        self.safety |= dynamics
        self.safety |= no_collide
    
    def set_progress(self):
        progress_str = None
        for (zgoal, xgoal) in self.progress_goals:
            if progress_str is not None:
                progress_str += " || (" + self.zstr + ' = ' + str(zgoal) + ' & ' + self.xstr + ' = ' + str(xgoal) + ") "
            else:
                progress_str = "(" + self.zstr + ' = ' + str(zgoal) + ' & ' + self.xstr + ' = ' + str(xgoal) + ") "
        self.progress |= {progress_str}
    
    def set_env_progress_goals(self):
        '''
        This function ensures that the tester never blocks the system forever, and eventually
        a path to goal.
        '''
        self.progress_goals = [(1,2), (3,2)]
    
    def setup_specs(self, env_init):
        self.variables()
        self.set_env_progress_goals()
        self.set_init(env_init)
        self.set_safety()
        self.set_progress()


class sys_specs:
    def __init__(self, maze, env_zstr, env_xstr):
        self.maze = maze
        self.vars = {}
        self.init = set()
        self.safety = set()
        self.progress = set()
        self.zstr = 'z'
        self.xstr = 'x'
        self.env_zstr = env_zstr
        self.env_xstr = env_xstr
    
    def variables(self):
        # State indicated by: (z,x)
        self.vars[self.zstr] = (0, self.maze.len_z)
        self.vars[self.xstr] = (0, self.maze.len_x)
    
    def set_init(self):
        self.zinit, self.xinit = self.maze.init
        init_string = self.zstr + ' = ' + str(self.zinit) + ' & ' + self.xstr + ' = ' + str(self.xinit)
        self.init |= {init_string}

    def no_collide(self):
        no_collide_spec = set()
        for x in range(0,self.maze.len_x):
            for z in range(0,self.maze.len_z):
                no_collide_str = '!((' + self.env_zstr + ' = '+str(z)+' && '+ self.env_xstr + ' = '+str(x) +') && (' + self.zstr + ' = '+str(z)+' && '+ self.xstr + ' = '+str(x) +'))'
                no_collide_spec |= {no_collide_str}
        return no_collide_spec

    def set_safety(self):
        dynamics = self.maze.transition_specs(self.zstr, self.xstr)
        no_collide = self.no_collide()
        self.safety |= dynamics
        self.safety |= no_collide
    
    def set_progress(self):
        self.zgoal, self.xgoal = self.maze.goal
        progress_str = self.zstr + ' = ' + str(self.zgoal) + ' & ' + self.xstr + ' = ' + str(self.xgoal)
        self.progress |= {progress_str}
    
    def setup_specs(self):
        self.variables()
        self.set_init()
        self.set_safety()
        self.set_progress()

if __name__ == "__main__":
    mazefile = 'maze.txt'
    maze = MazeNetwork(mazefile)
    env_zstr = "env_z"
    env_xstr = "env_x"
    system = system_specs(maze, env_zstr, env_xstr)
    system.setup_specs()

    environment = env_specs(maze, system.zstr, system.xstr)
    env_init = (4,2)
    environment.setup_specs(env_init)
    st()
