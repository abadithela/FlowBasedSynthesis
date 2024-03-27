'''
System under test (quadruped) controller for reactive beaver rescue example.
'''
from utils.quadruped_interface import quadruped_move

import logging
from tulip import transys, spec, synth
from tulip import dumpsmach
import tulip.gridworld as gw
from ipdb import set_trace as st

class Agent:
    def __init__(self, name, init, goals, maze):
        self.name = name
        self.init = init
        self.goals = list(set(goals))
        self.index = 0
        self.s = init
        self.maze = maze
        self.controller = self.find_controller(self.init)

    def set_maze(self, maze):
        self.maze = maze

    def find_controller(self, init):
        print('------- (Re-)synthesizing the agent\'s controller -------')
        logging.basicConfig(level=logging.WARNING)
        logging.getLogger('tulip.spec.lexyacc').setLevel(logging.WARNING)
        logging.getLogger('tulip.synth').setLevel(logging.WARNING)
        logging.getLogger('tulip.interfaces.omega').setLevel(logging.WARNING)

        sys_vars = {}
        sys_vars['s'] = (0, len(self.maze.states))
        sys_init = {'s = '+str(self.maze.inv_map[init])}
        sys_prog = set()
        goalstr = '(s = '+str(self.maze.inv_map[self.goals[0]])+')'
        for goal in self.goals[1:]:
            goalstr += ' || (s = '+str(self.maze.inv_map[goal])+')'
        sys_prog = goalstr
        sys_safe = set()
        sys_safe |= self.maze.transition_specs('s') # add the dynamics for the system

        env_vars = {}
        env_safe = set()
        env_init = {}
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
        self.index += 1

        exe_globals = dict()
        exec(dumpsmach.python_case(ctrl, classname='AgentCtrl'), exe_globals)
        M = exe_globals['AgentCtrl']()  # previous line creates the class `AgentCtrl`
        print('------- Controller available -------')
        # controller_namestr = "system_controller"+str(self.index)+".py"
        # dumpsmach.write_python_case(controller_namestr, ctrl, classname="AgentCtrl")
        self.controller = M
        return M
