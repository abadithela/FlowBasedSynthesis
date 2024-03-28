
import sys
sys.path.append('../..')

from reactive_examples.utils.get_graphs import get_graphs_from_network
from problem_data import *
from reactive_examples.utils.setup_logger import setup_logger
from reactive_examples.utils.custom_network import CustomNetwork
from optimization.milp_reactive_gurobipy import solve_max_gurobi
from components.setup_graphs import setup_nodes_and_edges

# For comparison to ICRA paper results
from beaver_rescue.pyomo_bilevel import solve_bilevel

def compare_runtimes(network):
    logger = setup_logger("simple_gridworld")
    # MILP
    print('========= Setup Graphs ==========')
    virtual, system, b_pi, virtual_sys = get_graphs_from_network(SYS_FORMULA, TEST_FORMULA, network, INIT, INTS, GOALS, logger)
    GD, SD = setup_nodes_and_edges(virtual, virtual_sys, b_pi)

    print('========= MILP ==========')
    exit_status, ftest, d, flow = solve_max_gurobi(GD, SD)
    milp_cuts = [x for x in d.keys() if d[x] == 1.0]
    print('Cut {} edges in the virtual game graph.'.format(len(milp_cuts)))
    print('The max flow through I is {}'.format(flow))

    # Bilevel opt with pyomo
    print('========= Pyomo ==========')
    cleaned_int = [int for int in GD.int if int not in GD.sink]
    f1_e, f2_e, f3_e, d_e, F, bilevel_runtime = solve_bilevel(GD, SD)
    bilevel_cuts = [x for x in d_e.keys() if d_e[x] >= 0.9 ]
    bypass = sum(f3_e[edge] for edge in GD.edges if edge[1] in GD.sink and edge[0] not in GD.sink)
    print('Cut {} edges in the virtual game graph.'.format(len(bilevel_cuts)))
    print('The max flow through I is {}'.format(F))
    print('Runtime {} s'.format(bilevel_runtime))



if __name__ == '__main__':
    states = ['init', 'p1', 'p2', 'p3', 'jump1', 'stand1', 'stand2', 'stand3', 'lie3',\
    'd1_j', 'd1_s', 'd2_s', 'd3_s', 'd3_l', 'goal']
    transitions = [('init', 'p1'), ('init', 'p2'), ('init', 'p3'), \
    ('p1', 'jump1'), ('p1', 'stand1'), ('p2', 'stand2'), ('p3', 'stand3'), ('p3', 'lie3'), \
    ('jump1', 'd1_j'),('stand1', 'd1_s'), ('stand2', 'd2_s'), ('stand3', 'd3_s'), ('lie3', 'd3_l'), \
    ('d1_s', 'p1'), ('d1_j', 'p1'),\
    ('d2_s', 'p2'), \
    ('d3_s', 'p3'), ('d3_l', 'p3'),\
    ('p2', 'p1'), ('p3', 'p2'), ('p1', 'p2'), ('p2', 'p3'), \
    ('d1_s', 'goal'), ('d1_j', 'goal'), ('d2_s', 'goal'), ('d3_s', 'goal'),  ('d3_l', 'goal')]


    network = CustomNetwork(states, transitions)

    compare_runtimes(network)
