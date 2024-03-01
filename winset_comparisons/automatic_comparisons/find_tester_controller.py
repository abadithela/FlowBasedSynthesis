import logging
from tulip import transys, spec, synth
from tulip import dumpsmach
from ipdb import set_trace as st
from utils import AugMazeNetwork, get_test_vars, get_test_init, get_test_safety_static, relate_edge_cuts_to_system_moves, plot_sol

class TesterCtrl:
    def __init__(self, maze):
        self.maze = maze
        self.controller = self.find_controller()

    def move(self, sys_pos):
        output = self.controller.move(sys_pos[1], sys_pos[0])
        # print(output)
        return output

    def find_controller(self):
        # try:
        #     # load the controller
        #     from tester_controller import TesterCtrl
        #     self.controller = TesterCtrl()
        #     print('successfully loaded tester controller')
        # except:

        logging.basicConfig(level=logging.WARNING)
        logging.getLogger('tulip.spec.lexyacc').setLevel(logging.WARNING)
        logging.getLogger('tulip.synth').setLevel(logging.WARNING)
        logging.getLogger('tulip.interfaces.omega').setLevel(logging.WARNING)

        test_vars = get_test_vars(self.maze)
        test_vars['auxI'] = (0,1)

        test_init = get_test_init(self.maze)
        test_init |= {'auxI = 0'}

        test_safety = get_test_safety_static(self.maze)

        # auxI dynamics
        test_safety |= {'auxI = 1 -> X(auxI = 1)'}
        int_str = ''
        for intermed in self.maze.intermed:
            int_str += '(z = '+str(intermed[0])+' && x = '+str(intermed[1])+') || '
        int_str = int_str[:-4]
        test_safety |= {'(auxI = 0 && ('+int_str+')) -> X(auxI = 1)'}
        test_safety |= {'(auxI = 0 && !('+int_str+')) -> X(auxI = 0)'}
        
        # have you seen I
        test_progress = set()
        # test_progress |= {'(auxI = 1)'}
        goal_str = ''
        for goal in self.maze.goal:
            goal_str += 'x = '+str(goal[1])+' && z = '+str(goal[0])+' || '
        goal_str = goal_str[:-4]
        test_progress |= {goal_str}
        test_safety |= {'!(auxI=1)'}

        sys_vars = {}
        sys_vars['x'] = (0,self.maze.len_x)
        sys_vars['z'] = (0,self.maze.len_z)

        sys_init = set()
        sys_init |= {'x = '+str(self.maze.init[1])+' && z = '+str(self.maze.init[0])}

        sys_safety = set()
        # add the dynamics for the system
        sys_safety |=  self.maze.augmented_dynamics_specs('x','z')
        # relate the edge cuts
        sys_safety |= relate_edge_cuts_to_system_moves(self.maze)
        # sys_safety |= {'(x = 2 && z=2) -> X()'}

        sys_progress = set()
        goal_str = ''
        for goal in self.maze.goal:
            goal_str += 'x = '+str(goal[1])+' && z = '+str(goal[0])+' || '
        goal_str = goal_str[:-4]
        sys_progress |= {goal_str}

        spc = spec.GRSpec(sys_vars, test_vars, sys_init, test_init,
                        sys_safety, test_safety, sys_progress, test_progress)

        print(spc.pretty())

        spc.moore = True # moore machine
        spc.qinit = r'\A \E'
        # spc.plus_one = True

        if not synth.is_realizable(spc, solver='omega'):
            print("Not realizable.")
            st()
        else:
            ctrl = synth.synthesize(spc, solver='omega', rm_deadends = 0)
        # dunp the controller
        controller_namestr = "tester_controller.py"
        dumpsmach.write_python_case(controller_namestr, ctrl, classname="TesterCtrl")

        exe_globals = dict()
        exec(dumpsmach.python_case(ctrl, classname='TesterCtrl'), exe_globals)
        M = exe_globals['TesterCtrl']()  # previous line creates the class `AgentCtrl`
        self.controller = M
        return self.controller

if __name__ == "__main__":
    mazefile = 'maze.txt'
    maze = AugMazeNetwork(mazefile)
    tester = TesterCtrl(maze)
    initpos = maze.init
    output = tester.move(initpos)
    plot_sol(output, maze)
