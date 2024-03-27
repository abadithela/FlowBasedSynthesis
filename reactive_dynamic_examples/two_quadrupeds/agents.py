from __future__ import print_function
import logging
from tulip import transys, spec, synth
from tulip import dumpsmach
from ipdb import set_trace as st
import sys
sys.path.append('..')
from components.maze_network import MazeNetwork
from tester_spec import get_tester_spec


class Tester:
    def __init__(self, name, system_init, tester_init, maze):
        self.name = name
        self.z = tester_init["z"]
        self.x = tester_init["x"]
        self.q = (self.z, self.x) # Tester state
        self.system_position = (system_init["z"], system_init["x"])
        self.qhist = 0 # DOUBLE-CHECK that 0 is always default state of automaton.
        self.maze = maze
        self.turn = 0
        self.GD = None
        self.SD = None
        self.cuts = None
        self.controller = None

    def set_optimization_results(self,cuts, GD, SD):
        self.set_GD(GD)
        self.set_cuts(cuts)
        self.set_SD(SD)

    def set_SD(self,SD):
        self.SD = SD

    def set_GD(self, GD):
        self.GD = GD

    def set_cuts(self, cuts):
        self.cuts = cuts

    def update_trace(self, system_position):
        '''
        Determines how the history variable 'q' changes.
        '''
        node = (self.system_position, 'q'+str(self.qhist)) # Node before system transitions
        edge_list = list(self.GD.graph.edges(self.GD.inv_node_dict[node]))
        self.system_position = system_position # update state
        if node[0] != (0,4):
            for edge in edge_list:
                in_node = self.GD.node_dict[edge[1]]
                in_state = in_node[0]
                in_q = in_node[-1]
                if in_state == system_position:
                    self.qhist = int(in_q[1:])
                    break

            assert("Error: Could not update q.")

    def manual_move(self,cell):
        (self.z, self.x) = cell
        self.q = (self.z, self.x)

    def tester_move(self, system_pos):
        self.update_trace(system_pos)
        sys_x = self.system_position[1]
        sys_z = self.system_position[0]
        try:
            assert system_pos == (sys_z, sys_x)
        except:
            st()
        output = self.controller.move(sys_x,sys_z, self.qhist)
        self.x = output['X_t']
        self.z = output['Z_t']
        self.turn = output['turn']
        self.q = (self.z,self.x)
        # print(output)
        # interface the tester quadruped here (only when it was the quadruped's turn)

    def find_controller(self, load_sol = False):

        if load_sol:
            try:
                # load the controller
                from tester_controller import TesterCtrl
                self.controller = TesterCtrl()
                print('successfully loaded tester controller')
                return
            except:
                pass

        print('synthesizing tester controller')
        logging.basicConfig(level=logging.WARNING)
        logging.getLogger('tulip.spec.lexyacc').setLevel(logging.WARNING)
        logging.getLogger('tulip.synth').setLevel(logging.WARNING)
        logging.getLogger('tulip.interfaces.omega').setLevel(logging.WARNING)

        specs = get_tester_spec(self.q, self.maze, self.GD, self.cuts)

        spc = spec.GRSpec(specs.env_vars, specs.vars, specs.env_init, specs.init,
                        specs.env_safety, specs.safety, specs.env_progress, specs.progress)

        print(spc.pretty())

        spc.moore = True # moore machine
        spc.qinit = r'\A \E'
        # spc.plus_one = True

        if not synth.is_realizable(spc, solver='omega'):
            print("Not realizable.")
            # st()
        else:
            ctrl = synth.synthesize(spc, solver='omega')
        # dunp the controller
        controller_namestr = "tester_controller.py"
        dumpsmach.write_python_case(controller_namestr, ctrl, classname="TesterCtrl")

        exe_globals = dict()
        exec(dumpsmach.python_case(ctrl, classname='TesterCtrl'), exe_globals)
        M = exe_globals['TesterCtrl']()  # previous line creates the class `AgentCtrl`
        self.controller = M

class Quadruped:
    def __init__(self, name, system_init, goal, maze, tester_init):
        self.name = name
        self.z = system_init["z"]
        self.x = system_init["x"]
        self.turn = 0
        self.s = (self.z, self.x)
        self.goal = goal
        self.index = 0
        self.maze = maze
        self.tester_init = tester_init
        self.controller = None

    def find_controller(self,maze):
        try:
            # load the controller
            from system_controller import AgentCtrl
            self.controller = AgentCtrl()
            print('successfully loaded system controller')
        except:
            print('synthesizing system controller')
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
            env_vars['Z_t'] = (-1,maze.len_z)
            env_vars['X_t'] = (0,maze.len_x)
            env_safe = set()
            # env_safe |= {'(X_t = 2 && Z_t = 1)'}
            env_init = {'Z_t = '+str(self.tester_init["z"])+' && X_t = '+str(self.tester_init["x"])}
            env_prog = set()
            env_prog |= {'(X_t = 2 && Z_t = 1) || (X_t = 2 && Z_t = 3) || (X_t = 2 && Z_t = 5) || (X_t = 2 && Z_t = -1)'} # tester will eventually make space
            # tester can move up and down the middle column
            dynamics_spec = {'(Z_t = 6) -> X((Z_t = 6) ||(Z_t = 5) || Z_t = -1)'}
            dynamics_spec |= {'(Z_t = 5) -> X((Z_t = 5) ||(Z_t = 4) || Z_t = 3)'}
            dynamics_spec |= {'(Z_t = 4) -> X((Z_t = 4) ||(Z_t = 3) || Z_t = 5)'}
            dynamics_spec |= {'(Z_t = 3) -> X((Z_t = 4) || (Z_t = 3) ||(Z_t = 2))'}
            dynamics_spec |= {'(Z_t = 2) -> X((Z_t = 3) || (Z_t = 2) ||(Z_t = 1))'}
            dynamics_spec |= {'(Z_t = 1) -> X((Z_t = 2) || (Z_t = 1) || (Z_t = 0))'}
            dynamics_spec |= {'(Z_t = 0) -> X((Z_t = 0) || (Z_t = 1)|| (Z_t = -1))'}
            dynamics_spec |= {'(Z_t = -1) -> X((Z_t = -1))'}
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
            controller_namestr = "system_controller.py"
            dumpsmach.write_python_case(controller_namestr, ctrl, classname="AgentCtrl")
            self.index += 1

            # print(dumpsmach.python_case(g, classname='AgentCtrl', start=))
            exe_globals = dict()
            exec(dumpsmach.python_case(ctrl, classname='AgentCtrl'), exe_globals)
            M = exe_globals['AgentCtrl']()  # previous line creates the class `AgentCtrl`
            self.controller = M

    def agent_move(self, tester_pos):
        output = self.controller.move(tester_pos[0],tester_pos[1])
        self.x = output['x']
        self.z = output['z']
        self.s = (self.z,self.x)

def next_move(tester, maze):
    maze.print_maze()
    pass
