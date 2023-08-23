import logging
import pdb
import networkx as nx
from tulip import transys, spec, synth

logging.basicConfig(level=logging.WARNING)
logging.getLogger('tulip.spec.lexyacc').setLevel(logging.WARNING)
logging.getLogger('tulip.synth').setLevel(logging.WARNING)
logging.getLogger('tulip.interfaces.omega').setLevel(logging.WARNING)

class Graph:
    def __init__(self):
        self.nstates = 14
        self.S = ["s"+str(k) for k in range(1,self.nstates+1)]
        self.S_sys = ["s1", "s3", "s5", "s7", "s9", "s11", "s13"]
        self.S_test = ["s2", "s4", "s6", "s8", "s10", "s12", "s14"]
        self.src = "s1"
        self.int = ["s6", "s9", "s10"]
        self.target = ["s9", "s10", "s13"]

    def gamegraph(self):
        self.G = nx.DiGraph()
        self.add_nodes_from(self.S)
        edges = [("s1", "s2"), ("s2", "s3"), ("s3", "s4"),
                ("s4", "s5"), ("s5", "s6"), ("s2", "s7"),
                ("s7", "s8"), ("s7", "s6"), ("s7", "s12"),
                ("s6", "s9"), ("s9", "s10"), ("s12", "s11"),
                ("s11", "s14"), ("s14", "s13"), ("s13", "s6")]
        self.G.add_edges_from(edges)

    def plot(self):
        G_agr = nx.nx_agraph.to_agraph(self.G)
        G_agr.node_attr['style'] = 'filled'
        G_agr.node_attr['gradientangle'] = 90

        for i in G_agr.nodes():
            n = G_agr.get_node(i)
            n.attr['shape'] = 'circle'
            
            if self.AP_dict[(i)] == spot.formula.ap("int"):
                n.attr['fillcolor'] = 'blue'
            if self.AP_dict[i] == spot.formula.ap("sink"):
                n.attr['fillcolor'] = 'yellow'
        G_agr.draw(fn+"_dot.pdf",prog='dot')
        pass
    
    def test_trans(self):
        self.Ttest = transys.FTS()
        test_states = ["test_"+str(k) for k in range(1, self.nstates/2+1)]
        self.Ttest.states.add_from(test_states)
        self.Ttest.states.initial.add('test_1')    # start in state test_1

    def sys_trans(self):
        # Create a finite transition system
        self.Tsys = transys.FTS()
        # Define the states of the system
        sys_states = ["sys_"+str(k) for k in range(1, self.nstates/2+1)]
        self.Tsys.states.add_from(sys_states)
        self.Tsys.states.initial.add('sys_1')    # start in state sys_1

        self.Tsys.transitions.add_comb({'X0'}, {'X1', 'X3'})
        sys.transitions.add_comb({'X1'}, {'X0', 'X4', 'X2'})
        sys.transitions.add_comb({'X2'}, {'X1', 'X5'})
        sys.transitions.add_comb({'X3'}, {'X0', 'X4'})
        sys.transitions.add_comb({'X4'}, {'X3', 'X1', 'X5'})
        sys.transitions.add_comb({'X5'}, {'X4', 'X2'})
        # @system_dynamics_section_end@

        # @system_labels_section@
        # Add atomic propositions to the states
        sys.atomic_propositions.add_from({'home', 'lot'})
        sys.states.add('X0', ap={'home'})
        sys.states.add('X5', ap={'lot'})
        # @system_labels_section_end@

        # @environ_section@
        env_vars = {'park'}
        env_init = set()                # empty set
        env_prog = '!park'
        env_safe = set()                # empty set
        
        sys_vars = {'X0reach'}          # infer the rest from TS
        sys_init = {'X0reach'}
        sys_prog = {'home'}             # []<>home
        sys_safe = {'(X (X0reach) <-> lot) || (X0reach && !park)'}
        sys_prog |= {'X0reach'}
        # @specs_setup_section_end@

        # @specs_create_section@
        # Create the specification
        specs = spec.GRSpec(env_vars, sys_vars, env_init, sys_init,
                            env_safe, sys_safe, env_prog, sys_prog)
        # Controller synthesis
        #
        # At this point we can synthesize the controller using one of the available
        # methods.
        #
        # @synthesize@
        # Moore machines
        # controller reads `env_vars, sys_vars`, but not next `env_vars` values
        specs.moore = True
        # synthesizer should find initial system values that satisfy
        # `env_init /\ sys_init` and work, for every environment variable
        # initial values that satisfy `env_init`.
        specs.qinit = r'\E \A'
        ctrl = synth.synthesize(specs, sys=sys)
        assert ctrl is not None, 'unrealizable'
        # @synthesize_end@

        #
        # Generate a graphical representation of the controller for viewing,
        # or a textual representation if dependencies for layout of DOT are missing.
        #
        # @plot_print@
        if not ctrl.save('discrete.png'):
            print(ctrl)

    def system_control_synt():
        pass

    def test_synt():
        pass