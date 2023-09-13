import sys
sys.path.append('..')
import numpy as np
from ipdb import set_trace as st
import networkx as nx
import pdb
from flow_constraints.optimization import solve_bilevel
from flow_constraints.construct_graphs import sys_test_sync
from flow_constraints.setup_graphs import GraphData, setup_nodes_and_edges

def call_pyomo(GD, S):

    ftest, fsys, d, F, f_on_s = solve_bilevel(GD, S)
    cuts = [x for x in d.keys() if d[x] >= 0.9]
    # pdb.set_trace()
    flow = F
    bypass_flow = sum([fsys[j] for j in fsys.keys() if j[1] in GD.sink])
    print('Cut {} edges in the virtual game graph.'.format(len(cuts)))
    print('The max flow through I is {}'.format(F))
    print('The bypass flow is {}'.format(bypass_flow))

    for cut in cuts:
        print('Cutting {0} to {1}'.format(GD.node_dict[cut[0]], GD.node_dict[cut[1]]))
    # st()
    return cuts, flow, bypass_flow, f_on_s

def highlight_cuts(cuts, GD, SD, virtual, virtual_sys):
    annot_cuts = [(GD.node_dict[cut[0]], GD.node_dict[cut[1]]) for cut in cuts]
    sys_cuts = [(GD.node_dict[cut[0]][0], GD.node_dict[cut[1]][0]) for cut in cuts]
    sys_cuts_annot = [((cut[0], q1), (cut[1], q2)) for cut in sys_cuts for q1 in virtual_sys.AP for q2 in virtual_sys.AP]

    virtual.plot_with_highlighted_edges(annot_cuts, "imgs/virtual_with_cuts")
    virtual_sys.plot_with_highlighted_edges(sys_cuts_annot, "imgs/virtual_sys_with_cuts")


def find_cuts():

    ints = [(2,0), (0,2), (2,4)]
    goals = [(0,0), (0,4)]

    virtual, system, b_pi, virtual_sys = sys_test_sync(ints, goals)


    GD, SD = setup_nodes_and_edges(virtual, virtual_sys, b_pi)

    cuts, flow, bypass, f_on_s = call_pyomo(GD, SD)

    annot_cuts = [(GD.node_dict[cut[0]], GD.node_dict[cut[1]]) for cut in cuts]
    sys_cuts = [(GD.node_dict[cut[0]][0], GD.node_dict[cut[1]][0]) for cut in cuts]
    sys_cuts_annot = [((cut[0], q1), (cut[1], q2)) for cut in sys_cuts for q1 in virtual_sys.AP for q2 in virtual_sys.AP]

    highlight_cuts(cuts, GD, SD, virtual, virtual_sys)

    st()

    return GD,cuts



if __name__ == '__main__':
    find_cuts()
