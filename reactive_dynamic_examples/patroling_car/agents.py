"""
Apurva:
1. Created Jan 17th to debug the script agents.py
2. Quadruped code works, but quadruped assumptions are not the same as the tester dynamics.
3. Tester code still needs to work.
"""

from __future__ import print_function
import logging
from tulip import transys, spec, synth
from tulip import dumpsmach
from ipdb import set_trace as st
import sys
from problem_data import *
sys.path.append('..')
from tester_spec_w_fuel import get_tester_spec

class Tester:
    def __init__(self, name, system_init, tester_init, maze):
        self.name = name
        self.z = tester_init["z"]
        self.x = tester_init["x"]
        self.q = (self.z, self.x) # Tester state
        self.system_position = (system_init["z"], system_init["x"])
        self.system_fuel = system_init["f"]
        self.qhist = 0 # DOUBLE-CHECK that 0 is always default state of automaton.
        self.maze = maze
        self.turn = 0
        self.GD = None
        self.cuts = None
        self.static_area = [state[0] for state in STATIC_AREA]
        self.controller = None

    def set_optimization_results(self,cuts, GD, SD):
        self.set_graphs(GD, SD)
        self.set_cuts(cuts)

    def set_graphs(self, GD, SD):
        self.GD = GD
        self.SD = SD

    def set_cuts(self, cuts):
        self.cuts = cuts

    def update_trace(self, system_position):
        '''
        Determines how the history variable 'q' changes.
        '''
        node = ((self.system_position, self.system_fuel), 'q'+str(self.qhist)) # Node before system transitions

        edge_list = list(self.GD.graph.edges(self.GD.inv_node_dict[node]))

        if system_position in self.maze.refuel:
            self.system_fuel = MAX_FUEL
        elif self.system_position == system_position:
            self.system_fuel = self.system_fuel
        else:
            self.system_fuel = self.system_fuel - 1
        self.system_position = system_position # update state
        if node[0][0] != (5,0):
            for edge in edge_list:
                in_node = self.GD.node_dict[edge[1]]
                in_state = in_node[0][0]
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
        sys_f = self.system_fuel
        try:
            assert system_pos == (sys_z, sys_x)
        except:
            st()
        output = self.controller.move(sys_x, sys_z, sys_f, self.qhist)
        self.x = output['X_t']
        self.z = output['Z_t']
        self.turn = output['turn']
        self.q = (self.z,self.x)
        print(output)
        # interface the tester quadruped here (only when it was the quadruped's turn)

    def find_controller(self, load_sol=True):
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

        # TODO: self.static_area has repeated pose states
        # reactive_cuts = [cut for cut in self.cuts if cut[0][0][0] not in self.static_area or cut[1][0][0] not in self.static_area]
        reactive_cuts = [cut for cut in self.cuts if cut[1][0][0] not in self.static_area]

        specs = get_tester_spec(self.q, self.maze, self.GD, self.SD, reactive_cuts)

        spc = spec.GRSpec(specs.env_vars, specs.vars, specs.env_init, specs.init,
                        specs.env_safety, specs.safety, specs.env_progress, specs.progress)

        print(spc.pretty())

        spc.moore = True # moore machine
        spc.qinit = r'\A \E'
        # spc.plus_one = True

        if not synth.is_realizable(spc, solver='omega'):
            print("Not realizable.")
            st()
        else:
            ctrl = synth.synthesize(spc, solver='omega')
        # dump the controller
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
        self.f = MAX_FUEL
        self.tester_init = tester_init
        self.unsafe = []
        self.controller = None #self.find_controller(maze)
        # maze.goal.append(goal)

    def resynthesize_controller(self,unsafe):
        self.unsafe.append(unsafe)
        print('synthesizing system controller')
        logging.basicConfig(level=logging.WARNING)
        logging.getLogger('tulip.spec.lexyacc').setLevel(logging.WARNING)
        logging.getLogger('tulip.synth').setLevel(logging.WARNING)
        logging.getLogger('tulip.interfaces.omega').setLevel(logging.WARNING)

        sys_vars = {}
        sys_vars['x'] = (0,self.maze.len_x)
        sys_vars['z'] = (0,self.maze.len_z)
        sys_vars['f'] = (0,MAX_FUEL)
        sys_init = {'x = '+str(self.x)+' && z = '+str(self.z)+' && f = '+str(self.f)}
        sys_prog = set()
        sys_prog |= {'(z = '+str(self.goal[0])+' && x = '+str(self.goal[1])+')'}
        sys_safe = set()
        # add the dynamics for the system
        dynamics_spec =  self.maze.dynamics_specs_w_fuel('x','z','f')
        sys_safe |= dynamics_spec

        # Safety spec, never run out of fuel
        sys_safe |= {'f > 0'}

        for unsafe_state in self.unsafe:
            sys_safe |= {'!(x = '+str(unsafe_state[1])+' && z = '+str(unsafe_state[0])+')'}


        env_vars = {}
        env_safe = set()
        env_init = set()
        env_prog = set()

        spc = spec.GRSpec(env_vars, sys_vars, env_init, sys_init,
                        env_safe, sys_safe, env_prog, sys_prog)

        # print(spc.pretty())
        spc.moore = False
        spc.qinit = r'\A \E'
        if not synth.is_realizable(spc, solver='omega'):
            print("Not realizable.")
            st()
        else:
            ctrl = synth.synthesize(spc, solver='omega')
        # dunp the controller
        self.index += 1
        controller_namestr = 'system_controller'+str(self.index)+'.py'
        dumpsmach.write_python_case(controller_namestr, ctrl, classname="AgentCtrl")

        # print(dumpsmach.python_case(g, classname='AgentCtrl', start=))
        exe_globals = dict()
        exec(dumpsmach.python_case(ctrl, classname='AgentCtrl'), exe_globals)
        M = exe_globals['AgentCtrl']()  # previous line creates the class `AgentCtrl`
        self.controller = M

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
            sys_vars['f'] = (0,MAX_FUEL)
            sys_init = {'x = '+str(self.x)+' && z = '+str(self.z)+' && f = '+str(self.f)}
            sys_prog = set()
            sys_prog |= {'(z = '+str(self.goal[0])+' && x = '+str(self.goal[1])+')'}
            sys_safe = set()
            # add the dynamics for the system
            dynamics_spec =  self.maze.dynamics_specs_w_fuel('x','z','f')
            sys_safe |= dynamics_spec
            # Safety spec, never run out of fuel
            sys_safe |= {'f > 0'}

            env_vars = {}
            env_safe = set()

            env_init = set()
            env_prog = set()

            spc = spec.GRSpec(env_vars, sys_vars, env_init, sys_init,
                            env_safe, sys_safe, env_prog, sys_prog)

            # print(spc.pretty())
            spc.moore = False
            spc.qinit = r'\A \E'
            if not synth.is_realizable(spc, solver='omega'):
                print("Not realizable.")
                st()
            else:
                ctrl = synth.synthesize(spc, solver='omega')
            self.index += 1
            # dunp the controller
            controller_namestr = "system_controller"+str(self.index)+".py"
            dumpsmach.write_python_case(controller_namestr, ctrl, classname="AgentCtrl")

            # print(dumpsmach.python_case(g, classname='AgentCtrl', start=))
            exe_globals = dict()
            exec(dumpsmach.python_case(ctrl, classname='AgentCtrl'), exe_globals)
            M = exe_globals['AgentCtrl']()  # previous line creates the class `AgentCtrl`
            self.controller = M

    def agent_move(self, tester_pos):
        output = self.controller.move()
        self.x = output['x']
        self.z = output['z']
        self.f = output['f']
        self.s = ((self.z,self.x), self.f)

    def agent_manual_move(self, sys_pos):
        self.z = sys_pos[0][0]
        self.x = sys_pos[0][1]
        self.f = sys_pos[-11]
        self.s = ((self.z,self.x), self.f)
