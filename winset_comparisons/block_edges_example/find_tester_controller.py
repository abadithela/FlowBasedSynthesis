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
        test_vars['edge01'] = (0,1)
        test_vars['edge12'] = (0,1)
        test_vars['edge23'] = (0,1)
        test_vars['edge25'] = (0,1)
        test_vars['edge28'] = (0,1)
        test_vars['edge34'] = (0,1)
        test_vars['edge36'] = (0,1)
        test_vars['edge47'] = (0,1)
        test_vars['edge56'] = (0,1)
        test_vars['edge67'] = (0,1)
        test_vars['edge89'] = (0,1)
        test_vars['auxI'] = (0,1)

        test_init = set()
        test_init |= {'(edge01 = 0 || edge01 = 1)'}
        test_init |= {'(edge12 = 0 || edge12 = 1)'}
        test_init |= {'(edge23 = 0 || edge23 = 1)'}
        test_init |= {'(edge25 = 0 || edge25 = 1)'}
        test_init |= {'(edge28 = 0 || edge28 = 1)'}
        test_init |= {'(edge34 = 0 || edge34 = 1)'}
        test_init |= {'(edge36 = 0 || edge36 = 1)'}
        test_init |= {'(edge47 = 0 || edge47 = 1)'}
        test_init |= {'(edge56 = 0 || edge56 = 1)'}
        test_init |= {'(edge67 = 0 || edge67 = 1)'}
        test_init |= {'(edge89 = 0 || edge89 = 1)'}

        test_init |= {'auxI = 0'}

        test_safety = set()
        test_safety |= {'edge01 = 0 -> X(edge01 = 0)'}
        test_safety |= {'edge12 = 0 -> X(edge12 = 0)'}
        test_safety |= {'edge23 = 0 -> X(edge23 = 0)'}
        test_safety |= {'edge25 = 0 -> X(edge25 = 0)'}
        test_safety |= {'edge28 = 0 -> X(edge28 = 0)'}
        test_safety |= {'edge34 = 0 -> X(edge34 = 0)'}
        test_safety |= {'edge36 = 0 -> X(edge36 = 0)'}
        test_safety |= {'edge47 = 0 -> X(edge47 = 0)'}
        test_safety |= {'edge56 = 0 -> X(edge56 = 0)'}
        test_safety |= {'edge67 = 0 -> X(edge67 = 0)'}
        test_safety |= {'edge89 = 0 -> X(edge89 = 0)'}
        test_safety |= {'edge01 = 1 -> X(edge01 = 1)'}
        test_safety |= {'edge12 = 1 -> X(edge12 = 1)'}
        test_safety |= {'edge23 = 1 -> X(edge23 = 1)'}
        test_safety |= {'edge25 = 1 -> X(edge25 = 1)'}
        test_safety |= {'edge28 = 1 -> X(edge28 = 1)'}
        test_safety |= {'edge34 = 1 -> X(edge34 = 1)'}
        test_safety |= {'edge36 = 1 -> X(edge36 = 1)'}
        test_safety |= {'edge47 = 1 -> X(edge47 = 1)'}
        test_safety |= {'edge56 = 1 -> X(edge56 = 1)'}
        test_safety |= {'edge67 = 1 -> X(edge67 = 1)'}
        test_safety |= {'edge89 = 1 -> X(edge89 = 1)'}

        # auxI dynamics
        test_safety |= {'auxI = 1 -> X(auxI = 1)'}
        test_safety |= {'(auxI = 0 && cell = 3) -> X(auxI = 1)'}
        test_safety |= {'(auxI = 0 && !(cell = 3)) -> X(auxI = 0)'}

        # have you seen I
        test_progress = set()
        test_progress |= {'(auxI = 1)'}

        sys_vars = {}
        sys_vars['cell'] = (0,9)

        sys_init = set()
        sys_init |= {'cell = 2'}

        sys_safety = set()
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

        # edge cuts
        sys_safety |= {'(cell = 0 && edge01 = 1) -> X(!(cell = 1))'}
        sys_safety |= {'(cell = 1 && edge01 = 1) -> X(!(cell = 0))'}
        sys_safety |= {'(cell = 1 && edge12 = 1) -> X(!(cell = 2))'}
        sys_safety |= {'(cell = 2 && edge12 = 1) -> X(!(cell = 1))'}
        sys_safety |= {'(cell = 2 && edge23 = 1) -> X(!(cell = 3))'}
        sys_safety |= {'(cell = 3 && edge23 = 1) -> X(!(cell = 2))'}
        sys_safety |= {'(cell = 2 && edge25 = 1) -> X(!(cell = 5))'}
        sys_safety |= {'(cell = 5 && edge25 = 1) -> X(!(cell = 2))'}
        sys_safety |= {'(cell = 2 && edge28 = 1) -> X(!(cell = 8))'}
        sys_safety |= {'(cell = 8 && edge28 = 1) -> X(!(cell = 2))'}
        sys_safety |= {'(cell = 3 && edge34 = 1) -> X(!(cell = 4))'}
        sys_safety |= {'(cell = 4 && edge34 = 1) -> X(!(cell = 3))'}
        sys_safety |= {'(cell = 3 && edge36 = 1) -> X(!(cell = 6))'}
        sys_safety |= {'(cell = 6 && edge36 = 1) -> X(!(cell = 3))'}
        sys_safety |= {'(cell = 4 && edge47 = 1) -> X(!(cell = 7))'}
        sys_safety |= {'(cell = 7 && edge47 = 1) -> X(!(cell = 4))'}
        sys_safety |= {'(cell = 5 && edge56 = 1) -> X(!(cell = 6))'}
        sys_safety |= {'(cell = 6 && edge56 = 1) -> X(!(cell = 7))'}
        sys_safety |= {'(cell = 6 && edge67 = 1) -> X(!(cell = 7))'}
        sys_safety |= {'(cell = 7 && edge67 = 1) -> X(!(cell = 6))'}
        sys_safety |= {'(cell = 8 && edge89 = 1) -> X(!(cell = 9))'}
        sys_safety |= {'(cell = 9 && edge89 = 1) -> X(!(cell = 8))'}


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
