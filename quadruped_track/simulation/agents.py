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
        self.z = pos[0]
        self.x = pos[1]

    def move(self,cell):
        (self.z, self.x) = cell
        self.q = (self.z, self.x)

class Quadruped:
    def __init__(self, name, pos, goal, maze, tester):
        self.name = name
        self.s = pos
        self.z = pos[0]
        self.x = pos[1]
        self.goal = goal
        self.index = 0
        self.maze = maze
        self.controller = self.find_controller(maze, tester)

    def find_controller(self,maze,tester):
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
        # add collision constraints
        safe_spec = set()
        for x in range(0,maze.len_x):
            for z in range(0,maze.len_z):
                safe_spec |= {'!((z = '+str(z)+' && '+'x = '+str(x) +') && (Z_t = '+str(z)+' && '+'X_t = '+str(x)+'))'}
        sys_safe |= safe_spec

        env_vars = {}
        env_vars['Z_t'] = (0,maze.len_z)
        env_vars['X_t'] = (0,maze.len_x)
        env_safe = set()
        # env_safe |= {'(X_t = 2 && Z_t = 1)'}
        env_init = {'Z_t = '+str(tester.z)+' && X_t = '+str(tester.x)}
        env_prog = set()
        env_prog |= {'(X_t = 2 && Z_t = 1) || (X_t = 2 && Z_t = 3)'} # tester will eventually make space
        # tester can move up and down the middle column
        dynamics_spec = {'(Z_t = 4) -> X((Z_t = 4) ||(Z_t = 3))'}
        dynamics_spec |= {'(Z_t = 3) -> X((Z_t = 4) || (Z_t = 3) ||(Z_t = 2))'}
        dynamics_spec |= {'(Z_t = 2) -> X((Z_t = 3) || (Z_t = 2) ||(Z_t = 1))'}
        dynamics_spec |= {'(Z_t = 1) -> X((Z_t = 2) || (Z_t = 1))'}
        dynamics_spec |= {'(X_t = 2) -> X((X_t = 2))'}

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
