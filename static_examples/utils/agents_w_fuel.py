'''
System under test, controller for a static environment.
'''
from __future__ import print_function
import logging
from tulip import transys, spec, synth
from tulip import dumpsmach
from static_examples.utils.quadruped_interface import quadruped_move
from problem_data import MAX_FUEL

class Quadruped:
    def __init__(self, name, pos, goals, maze, aux_formula={'safe': None, 'init': None, 'prog': None, 'var': None}):
        self.name = name
        self.s = pos
        self.z = pos[0][0]
        self.x = pos[0][1]
        self.f = pos[-1]
        self.goals = set(goals)
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
        sys_vars['f'] = (0,MAX_FUEL)
        sys_init = {'x = '+str(self.x)+' && z = '+str(self.z)+' && f = '+str(self.f)}
        sys_prog = set()
        goalstr = ''
        reduced_GOALS = list(set([goal[0] for goal in self.goals]))
        for goal in reduced_GOALS:
            goalstr += '(z = '+str(goal[0])+' && x = '+str(goal[1])+') || '
        goalstr = goalstr[:-4]
        sys_prog |= {goalstr}
        sys_safe = set()

        # add the dynamics for the system
        dynamics_spec =  maze.dynamics_specs_w_fuel('x','z','f')
        sys_safe |= dynamics_spec

        # Safety spec, never run out of fuel
        sys_safe |= {'f > 0'}

        # add auxiliary formula (re-written reaction spec)
        if self.aux_formula['var']:
            for var in self.aux_formula['var']:
                sys_vars[var] = 'boolean'
        if self.aux_formula['safe']:
            sys_safe |= self.aux_formula['safe']
        if self.aux_formula['init']:
            sys_init |= self.aux_formula['init']
        if self.aux_formula['prog']:
            sys_prog |= self.aux_formula['prog']

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
        self.f = output['f']
        self.s = ((self.z,self.x), self.f)
        quadruped_move((self.z,self.x))
