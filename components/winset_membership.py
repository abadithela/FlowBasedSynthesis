# Script to check membership of a state in winning set.
from tulip import transys, spec, synth
from tulip.interfaces.omega import _grspec_to_automaton, _strategy_to_state_annotated
from omega.games import gr1

class WinSet:
    def __init__(self, spec=None, sys_spec=None, env_spec=None):
        if spec is None:
            self.sys_spec=sys_spec
            self.env_spec = env_spec
            self.spec = self.make_grspec()
        else:
        self.find_winset()
        
    def make_grspec(self):
        env_vars = self.env_spec.variables
        sys_vars = self.sys_spec.variables
        env_init = self.env_spec.init
        sys_init = self.sys_spec.init
        env_safe = self.env_spec.safety
        sys_safe = self.sys_spec.safety
        env_prog = self.env_spec.prog
        sys_prog = self.sys_spec.prog
        return spec.GRSpec(env_vars, sys_vars, env_init, sys_init,
                        env_safe, sys_safe, env_prog, sys_prog)

    def find_winset(self):
        self.aut = _grspec_to_automaton(self.spec)
        self.z, _, _ = gr1.solve_streett_game(self.aut)
        
    def check_membership(self, state_dict):
        check_bdd = self.aut.let(state_dict, self.z)
        if check_bdd == self.aut.true:
            return True
        elif check_bdd == self.aut.false:
            return False
        else:
            print("Boolean expression not returned")
    
    def compute_winset(self):
        sys_vars = list(self.sys_spec.vars.keys())
        env_vars = list(self.env_spec.vars.keys())
        
        pass

