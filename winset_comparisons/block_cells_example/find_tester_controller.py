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

        test_init = set()
        test_init |= {'(cell0 = 0 || cell0 = 1) && (cell1 = 0 || cell1 = 1) && (cell2 = 0 || cell2 = 1) && (cell3 = 0 || cell3 = 1) && (cell4 = 0 || cell4 = 1)'}

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


        test_progress = set()
        test_progress |= {'cell = 0'}

        sys_vars = {}
        sys_vars['cell'] = (0,4)

        sys_init = set()
        sys_init |= {'cell = 2'}

        sys_safety = set()
        # don't collide with blocked cell
        sys_safety |= {'!(cell = 0 && cell0 = 1) && !(cell = 1 && cell1 = 1) && !(cell = 2 && cell2 = 1) && !(cell = 3 && cell3 = 1) && !(cell = 4 && cell4 = 1)'}
        # dynamics
        sys_safety |= {'cell = 0 -> X(cell = 0 || cell = 1)'}
        sys_safety |= {'cell = 1 -> X(cell = 0 || cell = 1 || cell = 2)'}
        sys_safety |= {'cell = 2 -> X(cell = 1 || cell = 2 || cell = 3)'}
        sys_safety |= {'cell = 3 -> X(cell = 2 || cell = 3 || cell = 4)'}
        sys_safety |= {'cell = 4 -> X(cell = 3 || cell = 4)'}

        # sys_safety |= {'cell = 0 && cell1 = 1 -> X(!(cell = 1))'}
        # sys_safety |= {'cell = 1 && cell0 = 1 -> X(!(cell = 0))'}
        # sys_safety |= {'cell = 1 && cell2 = 1 -> X(!(cell = 2))'}
        # sys_safety |= {'cell = 2 && cell1 = 1 -> X(!(cell = 1))'}
        # sys_safety |= {'cell = 2 && cell3 = 1 -> X(!(cell = 3))'}
        # sys_safety |= {'cell = 3 && cell2 = 1 -> X(!(cell = 2))'}
        # sys_safety |= {'cell = 3 && cell4 = 1 -> X(!(cell = 4))'}
        # sys_safety |= {'cell = 4 && cell3 = 1 -> X(!(cell = 3))'}



        # sys_safety |= {'!(cell = 0)'}

        sys_progress = set()
        sys_progress |= {'cell = 0 || cell = 4'}


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
