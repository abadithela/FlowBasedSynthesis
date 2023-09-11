# Synthesizing a controller for the system
from __future__ import print_function
import logging
from tulip import transys, spec, synth
from tulip import dumpsmach
import sys
sys.path.append('..')
from maze_network import MazeNetwork
from system_specs import sys_specs, env_specs
from pdb import set_trace as st

class Quadruped_Tester:
    def __init__(self, name, maze=None, tester_init=None):
        self.name = name
        self.index = 0
        if maze is not None:
            self.maze = maze
            self.tester_init = tester_init
        else:
            self.default_setup()
        self.zstr = "env_z"
        self.xstr = "env_x"
        self.construct_sys_specs()
        self.construct_env_specs()
        self.s = self.maze.init
        self.z = self.maze.init[0]
        self.x = self.maze.init[1]
        
    def default_setup(self):
        mazefile = 'maze.txt'
        self.maze = MazeNetwork(mazefile)
        self.tester_init = (0,2)

    def set_intermediate_states(self, I1=(3,4), I2=(1,0)):
        self.I1 = I1
        self.I2 = I2

    def add_intermediate_dynamics(self):
        intermediate_dynamics = set()
        intermediate_dynamics |= {'I1 = 1 -> X(I1 = 1)'}
        intermediate_dynamics |= {'I2 = 1 -> X(I2 = 1)'}
        intermediate_dynamics |= {'I = 1 -> X(I = 1)'}
        intermediate_dynamics |= {'(I1 = 1 && I2 = 1) -> (I = 1)'}
        visited_I1 = {'('+ self.sys_zstr + '=' + str(self.I1[0]) + ' & ' + self.sys_xstr + '=' + str(self.I1[1]) +') -> (I1=1)'}
        visited_I2 = {'('+ self.sys_zstr + '=' + str(self.I2[0]) + ' & ' + self.sys_xstr + '=' + str(self.I2[1]) +') -> (I2=1)'}
        intermediate_dynamics |= visited_I1
        intermediate_dynamics |= visited_I2
        return intermediate_dynamics

    def add_intermediate_progress(self):
        intermediate_progress = {'I=1'}
        return intermediate_progress
    
    def not_stay_in_bad_states_forever(self):
        bad_states = [(0,2), (2,2), (4,2)]
        safety_specs = set()
        for (zbad, xbad) in bad_states:
            safety_str = '!('+ self.zstr + '=' + str(zbad) + ' & ' + self.xstr + '=' + str(xbad) +')'
            safety_specs |= {safety_str}
        return safety_specs

    def add_visit_intermed_specs(self):
        self.specs.vars["I1"] = (0,1)
        self.specs.vars["I2"] = (0,1)
        self.specs.vars["I"] = (0,1)
        self.specs.init |= {'I1 = 0 && I2 = 0 && I = 0'}
        self.specs.safety |= self.add_intermediate_dynamics()
        self.specs.progress |= self.not_stay_in_bad_states_forever()
        self.specs.progress |= self.add_intermediate_progress()

    def construct_sys_specs(self):
        self.sys_specs = sys_specs(self.maze, self.zstr, self.xstr)
        self.sys_specs.setup_specs()
    
    def construct_env_specs(self):
        self.specs = env_specs(self.maze, self.sys_specs.zstr, self.sys_specs.xstr)
        self.sys_zstr = self.sys_specs.zstr
        self.sys_xstr = self.sys_specs.xstr
        self.specs.setup_specs(self.tester_init)
        
    def synthesize_controller(self):
        self.set_intermediate_states()
        self.add_visit_intermed_specs()
        self.controller = self.find_controller(self.maze, self.specs)

    def find_controller(self,maze,tester):
        logging.basicConfig(level=logging.WARNING)
        logging.getLogger('tulip.spec.lexyacc').setLevel(logging.WARNING)
        logging.getLogger('tulip.synth').setLevel(logging.WARNING)
        logging.getLogger('tulip.interfaces.omega').setLevel(logging.WARNING)

        spc = spec.GRSpec(self.sys_specs.vars, self.specs.vars, self.sys_specs.init, self.specs.init, 
                        self.sys_specs.safety, self.specs.safety, self.sys_specs.progress, self.specs.progress)

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
        controller_namestr = "tester_controller"+str(self.index)+".py"
        dumpsmach.write_python_case(controller_namestr, ctrl, classname="TesterCtrl")
        # # load the controller
        # from controller_namestr import AgentCtrl
        # M = AgentCtrl()
        self.index += 1

        # print(dumpsmach.python_case(g, classname='AgentCtrl', start=))
        exe_globals = dict()
        exec(dumpsmach.python_case(ctrl, classname='TesterCtrl'), exe_globals)
        M = exe_globals['TesterCtrl']()  # previous line creates the class `AgentCtrl`
        return M

    def agent_move(self, system_pos):
        # st()
        output = self.controller.move(system_pos[0],system_pos[1])
        self.x = output['env_x']
        self.z = output['env_z']
        self.s = (self.z,self.x)
        st()
        # quadruped_move((self.y,self.x))

if __name__ == "__main__":
    quadruped = Quadruped_Tester(name="tulip_tester_quad")
    quadruped.synthesize_controller()
    quadruped.agent_move((4,0))
    st()

    