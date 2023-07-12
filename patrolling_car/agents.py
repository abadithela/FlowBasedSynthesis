'''
System and tester agents.
Josefine Graebener
July 2023
'''
from __future__ import print_function
import logging
from tulip import transys, spec, synth
from tulip import dumpsmach
from ipdb import set_trace as st
# from quadruped_interface import quadruped_move

class Tester:
    def __init__(self, name, pos):
        self.name = name
        self.q = pos
        self.x = pos[0]
        self.y = pos[1]

    def move(self,cell):
        (self.x, self.y) = cell
        self.q = (self.x, self.y)

class Car:
    def __init__(self, name, pos, goal, maze):
        self.name = name
        self.s = pos
        self.x = pos[0]
        self.y = pos[1]
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
        sys_vars['y'] = (0,maze.len_y)
        sys_init = {'x = ' + str(self.x)+' && y = ' + str(self.y)}
        sys_prog = set()
        sys_prog |= {'(x = ' + str(self.goal[0])+' && y = ' + str(self.goal[1]) + ')'}
        sys_safe = set()
        # add the dynamics for the system
        dynamics_spec =  maze.transition_specs('x','y')
        sys_safe |= dynamics_spec
        # add collision constraints
        safe_spec = set()
        # for x in range(0,maze.len_x):
        #     for y in range(0,maze.len_y):
        #         safe_spec |= {'!((x = '+str(x)+' && '+'y = '+str(y) +') && (X_t = '+str(x)+' && '+'Y_t = '+str(y)+'))'}
        sys_safe |= safe_spec

        env_vars = {}
        env_vars['X_t'] = (0,maze.len_x)
        # env_vars['Y_t'] = (0,maze.len_y)
        env_safe = set()
        env_init = {'X_t = '+str(maze.tester_init[0])}#+' && Y_t = '+str(maze.tester_init[1])}
        env_prog = set()
        env_safe |= {'(X_t = 1)'}#' && Y_t = 1)'}# || (X_t = 5 && Y_t = 1)'}
        # dynamics_spec =  maze.transition_specs('X_t','Y_t')
        # env_safe |= dynamics_spec

        spc = spec.GRSpec(env_vars, sys_vars, env_init, sys_init,
                        env_safe, sys_safe, env_prog, sys_prog)

        print(spc.pretty())

        spc.moore = False
        spc.qinit = r'\A \E'
        if not synth.is_realizable(spc, solver='omega'):
            print("Not realizable.")
            st()
        else:
            st()
            ctrl = synth.synthesize(spc, solver='omega')
        # dump the controller
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
        self.y = output['y']
        self.s = (self.x,self.y)
        # quadruped_move((self.y,self.x))
