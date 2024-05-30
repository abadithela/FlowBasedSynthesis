'''
System under test, controller for a static environment.
'''
from __future__ import print_function
import logging
from tulip import transys, spec, synth
from tulip import dumpsmach
from reactive_examples.utils.quadruped_interface import quadruped_move

class Quadruped:
    def __init__(self, name, pos, goals, maze, aux_formula={'safe': None, 'init': None, 'prog': None, 'var': None}):
        self.name = name
        self.s = pos
        self.z = pos[0]
        self.x = pos[1]
        self.goals = goals
        self.index = 0
        self.maze = maze
        self.aux_formula = aux_formula
        self.controller = None

    def find_controller(self, maze):
        self.maze = maze
        logging.basicConfig(level=logging.WARNING)
        logging.getLogger('tulip.spec.lexyacc').setLevel(logging.WARNING)
        logging.getLogger('tulip.synth').setLevel(logging.WARNING)
        logging.getLogger('tulip.interfaces.omega').setLevel(logging.WARNING)

        sys_vars = {}
        sys_vars['x'] = (0,maze.len_x)
        sys_vars['z'] = (0,maze.len_z)
        sys_init = {'x = '+str(self.x)+' && z = '+str(self.z)}
        sys_prog = set()
        goalstr = ''
        for goal in self.goals:
            goalstr += '(z = '+str(goal[0])+' && x = '+str(goal[1])+') || '
        goalstr = goalstr[:-4]
        sys_prog |= {goalstr}
        sys_safe = set()
        # add the dynamics for the system
        dynamics_spec =  maze.transition_specs('z','x')
        sys_safe |= dynamics_spec

        if self.aux_formula['var']:
            sys_vars[self.aux_formula['var']] = 'boolean'
        if self.aux_formula['safe']:
            sys_safe |= {self.aux_formula['safe']}
        if self.aux_formula['init']:
            sys_init |= {self.aux_formula['init']}
        if self.aux_formula['prog']:
            sys_prog |= {self.aux_formula['prog']}

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
        # # load the controller
        # from controller_namestr import AgentCtrl
        # M = AgentCtrl()
        self.index += 1

        # print(dumpsmach.python_case(g, classname='AgentCtrl', start=))
        exe_globals = dict()
        exec(dumpsmach.python_case(ctrl, classname='AgentCtrl'), exe_globals)
        M = exe_globals['AgentCtrl']()  # previous line creates the class `AgentCtrl`
        self.controller = M
        return M

    def agent_move(self):
        output = self.controller.move()
        self.x = output['x']
        self.z = output['z']
        self.s = (self.z,self.x)
        quadruped_move((self.z,self.x))
