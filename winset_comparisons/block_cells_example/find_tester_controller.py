import logging
from tulip import transys, spec, synth
from tulip import dumpsmach
from ipdb import set_trace as st

class TesterCtrl:
    def __init__(self):
        self.controller = self.find_controller()

    def move(self, sys_pos):
        output = self.controller.move(sys_pos)
        print(output)

    def find_controller(self):
        logging.basicConfig(level=logging.WARNING)
        logging.getLogger('tulip.spec.lexyacc').setLevel(logging.WARNING)
        logging.getLogger('tulip.synth').setLevel(logging.WARNING)
        logging.getLogger('tulip.interfaces.omega').setLevel(logging.WARNING)

        test_vars = {}
        test_vars['cell0'] = (0,1)
        test_vars['cell1'] = (0,1)
        test_vars['cell2'] = (0,1)
        test_vars['cell3'] = (0,1)
        test_vars['cell4'] = (0,1)
        test_vars['cell5'] = (0,1)
        test_vars['cell6'] = (0,1)
        test_vars['cell7'] = (0,1)
        test_vars['cell8'] = (0,1)
        test_vars['cell9'] = (0,1)
        test_vars['auxI'] = (0,1)

        test_init = set()
        test_init |= {'(cell0 = 0 || cell0 = 1) && (cell1 = 0 || cell1 = 1) && (cell2 = 0 || cell2 = 1) && (cell3 = 0 || cell3 = 1) && (cell4 = 0 || cell4 = 1)'}
        test_init |= {'(cell5 = 0 || cell5 = 1) && (cell6 = 0 || cell6 = 1) && (cell7 = 0 || cell7 = 1)'}
        test_init |= {'(cell8 = 0 || cell8 = 1) && (cell9 = 0 || cell9 = 1)'}

        test_init |= {'auxI = 0'}
        test_init |= {'cell2 = 0'}

        test_safety = set()
        test_safety |= {'cell0 = 0 -> X(cell0 = 0)'}
        test_safety |= {'cell0 = 1 -> X(cell0 = 1)'}
        test_safety |= {'cell1 = 0 -> X(cell1 = 0)'}
        test_safety |= {'cell1 = 1 -> X(cell1 = 1)'}
        test_safety |= {'cell2 = 0 -> X(cell2 = 0)'}
        test_safety |= {'cell2 = 1 -> X(cell2 = 1)'}
        test_safety |= {'cell3 = 0 -> X(cell3 = 0)'}
        test_safety |= {'cell3 = 1 -> X(cell3 = 1)'}
        test_safety |= {'cell4 = 0 -> X(cell4 = 0)'}
        test_safety |= {'cell4 = 1 -> X(cell4 = 1)'}
        test_safety |= {'cell5 = 0 -> X(cell5 = 0)'}
        test_safety |= {'cell5 = 1 -> X(cell5 = 1)'}
        test_safety |= {'cell6 = 0 -> X(cell6 = 0)'}
        test_safety |= {'cell6 = 1 -> X(cell6 = 1)'}
        test_safety |= {'cell7 = 0 -> X(cell7 = 0)'}
        test_safety |= {'cell7 = 1 -> X(cell7 = 1)'}
        test_safety |= {'cell8 = 0 -> X(cell7 = 0)'}
        test_safety |= {'cell8 = 1 -> X(cell7 = 1)'}
        test_safety |= {'cell9 = 0 -> X(cell7 = 0)'}
        test_safety |= {'cell9 = 1 -> X(cell7 = 1)'}

        test_safety |= {'auxI = 1 -> X(auxI = 1)'}
        test_safety |= {'(auxI = 0 && cell = 3) -> X(auxI = 1)'}
        test_safety |= {'(auxI = 0 && !(cell = 3)) -> X(auxI = 0)'}
        # test_safety |= {'!(cell = 4)'}

        test_progress = set()
        test_progress |= {'(auxI = 1)'}

        sys_vars = {}
        sys_vars['cell'] = (0,9)

        sys_init = set()
        sys_init |= {'cell = 2'}

        sys_safety = set()
        # don't collide with blocked cell
        sys_safety |= {'!(cell = 0 && cell0 = 1) && !(cell = 1 && cell1 = 1) && !(cell = 2 && cell2 = 1) && !(cell = 3 && cell3 = 1) && !(cell = 4 && cell4 = 1)'}
        sys_safety |= {'!(cell = 5 && cell5 = 1) && !(cell = 6 && cell6 = 1) && !(cell = 7 && cell7 = 1)'}
        sys_safety |= {'!(cell = 8 && cell8 = 1) && !(cell = 9 && cell9 = 1)'}
        # dynamics
        sys_safety |= {'cell = 0 -> X(cell = 0 || cell = 1)'}
        sys_safety |= {'cell = 1 -> X(cell = 0 || cell = 1 || cell = 2)'}
        sys_safety |= {'cell = 2 -> X(cell = 1 || cell = 2 || cell = 3 || cell = 5 || cell = 8)'}
        sys_safety |= {'cell = 3 -> X(cell = 2 || cell = 3 || cell = 4 || cell = 6)'}
        sys_safety |= {'cell = 4 -> X(cell = 4 || cell = 3 || cell = 7)'}
        sys_safety |= {'cell = 5 -> X(cell = 2 || cell = 5 || cell = 6)'}
        sys_safety |= {'cell = 6 -> X(cell = 5 || cell = 6 || cell = 7 || cell = 3)'}
        sys_safety |= {'cell = 7 -> X(cell = 6 || cell = 7 || cell = 4)'}
        sys_safety |= {'cell = 8 -> X(cell = 2 || cell = 8 || cell = 9)'}
        sys_safety |= {'cell = 9 -> X(cell = 9)'}

        sys_progress = set()
        sys_progress |= {'cell = 4 || cell = 0'}


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
        return M

if __name__ == "__main__":

    tester = TesterCtrl()
    output = tester.move(2)
    print(output)
    st()
