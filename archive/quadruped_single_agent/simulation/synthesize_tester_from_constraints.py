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
        else:
            self.default_maze()

        if tester_init is not None:
            self.tester_init = tester_init
        else:
            self.default_tester()
        self.zstr = "env_z"
        self.xstr = "env_x"
        self.construct_sys_specs()
        self.construct_env_specs()
        self.s = self.maze.init
        self.z = self.maze.init[0]
        self.x = self.maze.init[1]
        self.set_intermediate_states()
        self.add_visit_intermed_specs()
        
    def default_maze(self):
        mazefile = 'maze.txt'
        self.maze = MazeNetwork(mazefile)
        
    def default_tester(self):
        self.tester_init = (4,2)

    def set_intermediate_states(self, I1=(3,4), I2=(1,0)):
        self.I1 = I1
        self.I2 = I2
    
    def add_intermediate_dynamics(self):
        intermediate_dynamics = set()
        intermediate_dynamics |= {'I1 = 1 -> X(I1 = 1)'}
        intermediate_dynamics |= {'(I1 = 0 && ' + '!('+ self.sys_zstr + '=' + str(self.I1[0]) + ' & ' + self.sys_xstr + '=' + str(self.I1[1]) +')) -> X(I1 = 0)'}
        intermediate_dynamics |= {'I2 = 1 -> X(I2 = 1)'}
        intermediate_dynamics |= {'(I2 = 0 && ' + '!('+ self.sys_zstr + '=' + str(self.I2[0]) + ' & ' + self.sys_xstr + '=' + str(self.I2[1]) +')) -> X(I2 = 0)'}
        # intermediate_dynamics |= {'I = 1 -> X(I = 1)'}
        # intermediate_dynamics |= {'I1 = 0 -> I = 0'}
        # intermediate_dynamics |= {'I2 = 0 -> I = 0'}
        # intermediate_dynamics |= {'(I1 = 1 && I2 = 1) -> (I = 1)'}
        visited_I1 = {'('+ self.sys_zstr + '=' + str(self.I1[0]) + ' & ' + self.sys_xstr + '=' + str(self.I1[1]) +') -> X(I1=1)'}
        visited_I2 = {'('+ self.sys_zstr + '=' + str(self.I2[0]) + ' & ' + self.sys_xstr + '=' + str(self.I2[1]) +') -> X(I2=1)'}
        intermediate_dynamics |= visited_I1
        intermediate_dynamics |= visited_I2
        return intermediate_dynamics
    
    def add_visit_intermed_specs(self):
        self.specs.vars["I1"] = (0,1)
        self.specs.vars["I2"] = (0,1)
        # self.specs.vars["I"] = (0,1)
        self.specs.init |= {'I1 = 0 && I2 = 0'}
        self.specs.safety |= self.add_intermediate_dynamics()
        self.specs.safety |= self.not_stay_in_bad_states_forever()
        # self.specs.progress |= {'I1=1 && I2 = 1'}

    
    def not_stay_in_bad_states_forever(self):
        safety_specs = set()
        safety_str1 = {'!((z=4 && x=1) && (env_z=4 && env_x=2 && I1=0))'}
        safety_str2 = {'!((z=2 && x=3) && (env_z=2 && env_x=2 && I2=0))'}
        safety_specs |= safety_str1
        safety_specs |= safety_str2
        return safety_specs


    def add_constraints_from_opt(self):
        constraints = set()
        for (sys_state, tester_state, qstate) in self.opt_constraints:
            zsys, xsys = sys_state
            ztest, xtest = tester_state
            if qstate == "q0":
                constr = '((I1 = 0 && I2 = 0 && ('+ self.sys_zstr + '=' + str(zsys) + ' & ' + self.sys_xstr + '=' + str(xsys) +')) -> ('+ self.zstr + '=' + str(ztest) + ' & ' + self.xstr + '=' + str(xtest) +'))'
            elif qstate =="q3": 
                constr = '((I1 = 1 && I2 = 0 && ('+ self.sys_zstr + '=' + str(zsys) + ' & ' + self.sys_xstr + '=' + str(xsys) +')) -> ('+ self.zstr + '=' + str(ztest) + ' & ' + self.xstr + '=' + str(xtest) +'))'
            else:
                print("Something wrong in parsing optimization constraints")
                st()
            constraints |= {constr}
        self.specs.safety |= constraints
        return constraints

    def set_constraints_opt(self, constraints):
        """
        Function to set the quadruped system and quadruped tester 
        coordinates when found by the optimization. This is a list of 
        states: [(sys_coord, tester_coord)] such that when system is in 
        sys_coord and tester is in tester_coord, we add the tulip constraint that 
        'sys = sys_coord -> tester = tester_coord
        """
        self.opt_constraints = constraints

    def construct_sys_specs(self):
        self.sys_specs = sys_specs(self.maze, self.zstr, self.xstr)
        self.sys_specs.setup_specs()
    
    def construct_env_specs(self):
        self.specs = env_specs(self.maze, self.sys_specs.zstr, self.sys_specs.xstr)
        self.sys_zstr = self.sys_specs.zstr
        self.sys_xstr = self.sys_specs.xstr
        self.specs.setup_specs(self.tester_init)
        
    def synthesize_controller(self):

        constraints = self.add_constraints_from_opt()
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
        spc.plus_one = True

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
        print(output)
        # quadruped_move((self.y,self.x))

if __name__ == "__main__":
    quadruped = Quadruped_Tester(name="tulip_tester_quad")
    quadruped.synthesize_controller()
    quadruped.agent_move((4,0))
    st()

    