from __future__ import print_function
import logging
from tulip import transys, spec, synth
from tulip import dumpsmach
import tulip.gridworld as gw
from ipdb import set_trace as st
import random

class Blocker:
    def __init__(self, name, q):
        self.name = name
        self.q = q
        self.states = [1,2,3]
        self.transitions = {1: [1,2], 2: [1,2,3], 3: [2,3]}

    def random_move(self):
        if random.random() < 0.5:
            if self.q > 1:
                self.move_n()
            else:
                self.stay()
        else:
            if self.q < 3:
                self.move_s()
            else:
                self.stay()

    def move(self,cell):
        self.q = cell

    def move_n(self):
        self.q = self.q - 1

    def move_s(self):
        self.q = self.q + 1

    def stay(self):
        pass

class Runner:
    def __init__(self, name, s, goal):
        self.name = name
        self.s = s
        self.goal = goal
        self.index = 0
        # self.maze = maze
        self.controller = self.find_controller()

    def find_controller(self):
        logging.basicConfig(level=logging.WARNING)
        logging.getLogger('tulip.spec.lexyacc').setLevel(logging.WARNING)
        logging.getLogger('tulip.synth').setLevel(logging.WARNING)
        logging.getLogger('tulip.interfaces.omega').setLevel(logging.WARNING)

        #states
        sys_states = {0: [1,2,3], 1: [4], 2: [4], 3: [4], 4: [] }
        env_states = {1: [2], 2: [1,3], 3: [2]}
        env_init = 2

        sys_vars = {}
        sys_vars['s'] = (0,4)
        sys_init = {'s = '+str(self.s)}
        sys_prog = set()
        sys_prog |= {'(s = '+str(self.goal)+')'}
        sys_safe = set()
        # add the dynamics for the system
        dynamics_spec = set()
        for s in sys_states.keys():
            start = s
            next_steps_string = '(s = '+str(s)+')'
            for item in sys_states[s]:
                next_steps_string = next_steps_string + '|| (s = '+str(item)+')'
            dynamics_spec |= {'(s = '+str(s)+') -> X(('+ next_steps_string +'))'}
        sys_safe |= dynamics_spec
        # add collision constraints
        safe_spec = set()
        for q in env_states.keys(): # never be in the same state at once
            safe_spec |= {'!(s = '+str(q)+' && '+'q = '+str(q) +')'}
        for q in env_states.keys(): # never be in adjacent cells
            if q > 1:
                safe_spec |= {'!(s = '+str(q-1)+' && '+'q = '+str(q) +')'}
            if q < 3:
                safe_spec |= {'!(s = '+str(q+1)+' && '+'q = '+str(q) +')'}
        sys_safe |= safe_spec


        env_vars = {}
        env_vars['q'] = (1,3)
        env_safe = set()
        env_init = {'q = '+str(env_init)}
        env_prog = set()
        env_prog |= {'!(q = 2)'}

        # adding env dynamics
        dynamics_spec = set()
        for q in env_states.keys():
            start = q
            next_steps_string = '(q = '+str(q)+')'
            for item in env_states[q]:
                next_steps_string = next_steps_string + '|| (q = '+str(item)+')'
            dynamics_spec |= {'(q = '+str(q)+') -> X(('+ next_steps_string +'))'}
        env_safe |= dynamics_spec

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
        # controller_namestr = "robot_controller"+str(self.index)+".py"
        # dumpsmach.write_python_case(controller_namestr, ctrl, classname="AgentCtrl")
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
        output = self.controller.move(tester_pos)
        self.s = output['s']
