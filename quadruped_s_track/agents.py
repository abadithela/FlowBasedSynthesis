from __future__ import print_function
import logging
from tulip import transys, spec, synth
from tulip import dumpsmach
from ipdb import set_trace as st

class Tester:
    def __init__(self, name, pos):
        self.name = name
        self.q = pos
        self.z = pos[0]
        self.x = pos[1]

    def move(self,cell):
        (self.z, self.x) = cell
        self.q = (self.z, self.x)

class Quadruped:
    def __init__(self, name, pos, goal, maze):
        self.name = name
        self.s = pos
        self.z = pos[0]
        self.x = pos[1]
        self.goal = goal
        self.index = 0
        self.maze = maze
        self.controller = self.find_controller(maze)

    def find_controller(self,maze):
        logging.basicConfig(level=logging.WARNING)
        logging.getLogger('tulip.spec.lexyacc').setLevel(logging.WARNING)
        logging.getLogger('tulip.synth').setLevel(logging.WARNING)
        logging.getLogger('tulip.interfaces.omega').setLevel(logging.WARNING)

        sys_vars = {}
        sys_vars['x'] = (0,maze.len_x)
        sys_vars['z'] = (0,maze.len_z)
        sys_init = {'x = '+str(self.x)+' && z = '+str(self.z)}
        sys_prog = set()
        sys_prog |= {'(z = '+str(self.goal[0])+' && x = '+str(self.goal[1])+')'}
        sys_safe = set()
        # add the dynamics for the system
        dynamics_spec =  maze.transition_specs('z','x')
        sys_safe |= dynamics_spec

        env_vars = {}
        env_safe = set()
        env_init = set()
        env_prog = set()

        spc = spec.GRSpec(env_vars, sys_vars, env_init, sys_init,
                        env_safe, sys_safe, env_prog, sys_prog)

        print(spc.pretty())

        spc.moore = False
        spc.qinit = r'\A \E'
        if not synth.is_realizable(spc, solver='omega'):
            print("Not realizable.")
            st()
        else:
            ctrl = synth.synthesize(spc, solver='omega')
        # dunp the controller
        controller_namestr = "robot_controller"+str(self.index)+".py"
        dumpsmach.write_python_case(controller_namestr, ctrl, classname="AgentCtrl")
        self.index += 1

        exe_globals = dict()
        exec(dumpsmach.python_case(ctrl, classname='AgentCtrl'), exe_globals)
        M = exe_globals['AgentCtrl']()  # previous line creates the class `AgentCtrl`
        return M

    def agent_move(self):
        output = self.controller.move()
        self.x = output['x']
        self.z = output['z']
        self.s = (self.z,self.x)

        # output = self.controller.move()
        # print('Agent moving to {}'.format(self.network.map[output['s']]))
        # self.s = self.network.map[output['s']]
