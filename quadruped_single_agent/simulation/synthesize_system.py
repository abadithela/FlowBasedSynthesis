# Synthesizing a controller for the system
from __future__ import print_function
import logging
from tulip import transys, spec, synth
from tulip import dumpsmach
import sys
sys.path.append('..')
from maze_network import MazeNetwork
from pdb import set_trace as st
from system_specs import sys_specs, env_specs

class Quadruped:
    def __init__(self, name, maze=None, env_init=None):
        self.name = name
        self.index = 0
        if maze is not None:
            self.maze = maze
            self.env_init = env_init
        else:
            self.default_setup()
        self.env_zstr = "env_z"
        self.env_xstr = "env_x"
        self.construct_sys_specs()
        self.construct_env_specs()
        self.s = self.maze.init
        self.z = self.maze.init[0]
        self.x = self.maze.init[1]
        self.controller = self.find_controller(self.maze, self.env)
        

    def default_setup(self):
        mazefile = 'maze.txt'
        self.maze = MazeNetwork(mazefile)
        self.env_init = (4,2)

    def construct_sys_specs(self):
        self.specs = sys_specs(self.maze, self.env_zstr, self.env_xstr)
        self.specs.setup_specs()
    
    def construct_env_specs(self):
        self.env = env_specs(self.maze, self.specs.zstr, self.specs.xstr)
        self.env.setup_specs(self.env_init)
        
    def find_controller(self,maze,tester):
        logging.basicConfig(level=logging.WARNING)
        logging.getLogger('tulip.spec.lexyacc').setLevel(logging.WARNING)
        logging.getLogger('tulip.synth').setLevel(logging.WARNING)
        logging.getLogger('tulip.interfaces.omega').setLevel(logging.WARNING)

        spc = spec.GRSpec(self.env.vars, self.specs.vars, self.env.init, self.specs.init,
                        self.env.safety, self.specs.safety, self.env.progress, self.specs.progress)

        print(spc.pretty())
        spc.moore = False
        spc.qinit = r'\A \E'
        spc.plus_one = False

        if not synth.is_realizable(spc, solver='omega'):
            print("Not realizable.")
            st()
        else:
            ctrl = synth.synthesize(spc, solver='omega')
        # dunp the controller
        controller_namestr = "robot_controller"+str(self.index)+".py"
        dumpsmach.write_python_case(controller_namestr, ctrl, classname="AgentCtrl")
        # # load the controller
        # from controller_namestr import AgentCtrl
        # M = AgentCtrl()
        self.index += 1

        # print(dumpsmach.python_case(g, classname='AgentCtrl', start=))
        exe_globals = dict()
        exec(dumpsmach.python_case(ctrl, classname='AgentCtrl'), exe_globals)
        M = exe_globals['AgentCtrl']()  # previous line creates the class `AgentCtrl`
        return M

    def agent_move(self, tester_pos):
        # st()
        output = self.controller.move(tester_pos[0],tester_pos[1])
        self.x = output['x']
        self.z = output['z']
        self.s = (self.z,self.x)
        # quadruped_move((self.y,self.x))

if __name__ == "__main__":
    quadruped = Quadruped(name="sys_quad")