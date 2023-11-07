from __future__ import print_function
import logging
from tulip import transys, spec, synth
from tulip import dumpsmach
from ipdb import set_trace as st
import sys
sys.path.append('..')
from maze_network import MazeNetwork
from tester_spec import get_tester_spec
# from quadruped_interface import quadruped_move
from find_cuts_two_flows.find_cuts import setup_nodes_and_edges
from construct_automata.main import quad_test_sync

class Tester:
    def __init__(self, name, pos, maze, GD, cuts):
        self.name = name
        self.q = pos
        self.z = pos[0]
        self.x = pos[1]
        self.maze = maze
        self.turn = 0
        self.GD = GD
        self.cuts = cuts
        self.controller = self.find_controller()

    def manual_move(self,cell):
        (self.z, self.x) = cell
        self.q = (self.z, self.x)

    def tester_move(self, system_pos):
        output = self.controller.move(system_pos[0],system_pos[1])
        self.x = output['env_x']
        self.z = output['env_z']
        self.turn = output['turn']
        self.s = (self.z,self.x)
        print(output)

    def find_controller(self):
        logging.basicConfig(level=logging.WARNING)
        logging.getLogger('tulip.spec.lexyacc').setLevel(logging.WARNING)
        logging.getLogger('tulip.synth').setLevel(logging.WARNING)
        logging.getLogger('tulip.interfaces.omega').setLevel(logging.WARNING)

        specs = get_tester_spec(self.q, self.maze, self.GD, self.cuts)

        spc = spec.GRSpec(specs.env_vars, specs.vars, specs.env_init, specs.init,
                        specs.env_safety, specs.safety, specs.env_progress, specs.progress)

        print(spc.pretty())

        spc.moore = False # moore machine
        spc.qinit = r'\A \E'
        # spc.plus_one = True

        if not synth.is_realizable(spc, solver='omega'):
            print("Not realizable.")
            st()
        else:
            ctrl = synth.synthesize(spc, solver='omega')
        # dunp the controller
        controller_namestr = "tester_controller.py"
        dumpsmach.write_python_case(controller_namestr, ctrl, classname="TesterCtrl")

        exe_globals = dict()
        exec(dumpsmach.python_case(ctrl, classname='TesterCtrl'), exe_globals)
        M = exe_globals['TesterCtrl']()  # previous line creates the class `AgentCtrl`
        return M

class Quadruped:
    def __init__(self, name, pos, goal, maze, tester_init):
        self.name = name
        self.s = pos
        self.z = pos[0]
        self.x = pos[1]
        self.goal = goal
        self.index = 0
        self.maze = maze
        self.controller = self.find_controller(maze, tester_init)

    def find_controller(self,maze,tester_init):
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
        env_init = {'Z_t = '+str(tester_init["z"])+' && X_t = '+str(tester_init["x"])}
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

def next_move(tester, maze):
    maze.print_maze()
    
    pass

if __name__ == "__main__":
    mazefile = 'maze.txt'
    maze = MazeNetwork(mazefile)
    virtual, system, b_pi, virtual_sys = quad_test_sync()
    GD, SD = setup_nodes_and_edges(virtual, virtual_sys, b_pi)

    cuts = [(((4, 2), 'q0'), ((3, 2), 'q0')), (((2, 2), 'q3'), ((1, 2), 'q3'))]
    tester_init = {"z": 1, "x": 2}
    tester = Tester("tester", (1,2), maze, GD, cuts)
    sys_quad = Quadruped("sys_quad", (4,0), (0,0), maze, tester_init)
    st()
