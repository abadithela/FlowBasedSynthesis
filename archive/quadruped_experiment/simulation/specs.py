import sys
sys.path.append('..')
from maze_network import MazeNetwork
from pdb import set_trace as st

class system_specs:
    def __init__(self, maze):
        self.maze = maze
        self.vars = {}
        self.init = set()
        self.safety = set()
        self.progress = set()
        self.zstr = 'z'
        self.xstr = 'x'
    
    def variables(self):
        # State indicated by: (z,x)
        self.vars[self.zstr] = (0, self.maze.len_z)
        self.vars[self.xstr] = (0, self.maze.len_x)
    
    def set_init(self):
        self.zinit, self.xinit = self.maze.init
        init_string = self.zstr + ' = ' + str(self.zinit) + ' & ' + self.xstr + ' = ' + str(self.xinit)
        self.init |= {init_string}
    
    def set_safety(self):
        dynamics = self.maze.transition_specs(self.zstr, self.xstr)
        self.safety |= dynamics
    
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
    system = system_specs(maze)
    system.setup_specs()
    st()
