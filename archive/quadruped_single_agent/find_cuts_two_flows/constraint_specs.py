'''
Parse the cuts from the optimization for the tulip spec.
'''
from ipdb import set_trace as st

def get_history_vars(GD):
    '''
    Setting the history variable 'q' and its range.
    '''
    qs = list(set([GD.node_dict[node][-1] for node in list(GD.nodes)]))
    vals = [str(q[1:]) for q in qs]
    range = [int(min(vals)), int(max(vals))]
    var_dict = {'q': range}
    return var_dict

def history_var_dynamics(GD):
    '''
    Determines how the history variable 'q' changes.
    '''
    sys_z = 'Z'
    sys_x = 'X'
    q_str = 'q'
    hist_var_dyn = set()
    for node in list(GD.graph.nodes):
        out_node = GD.node_dict[node]
        out_state = out_node[0]
        out_q = out_node[-1]

        next_state_str = ''
        current_state = '('+sys_z+'= '+str(out_state[0])+' & '+sys_x+' = '+str(out_state[1])+' & '+q_str+' = '+str(out_q[1:])+')'
        edge_list = list(GD.graph.edges(node))
        for edge in edge_list:
            in_node = GD.node_dict[edge[1]]
            in_state = in_node[0]
            in_q = in_node[-1]
            next_state_str = next_state_str+'('+sys_z+'= '+str(in_state[0])+' & '+sys_x+' = '+str(in_state[1])+' & '+q_str+' = '+str(in_q[1:])+') || '

        next_state_str = next_state_str[:-4]
        hist_var_dyn |=  { current_state + ' -> X(' + next_state_str + ')'}
    return hist_var_dyn

def occupy_cuts(GD, cuts):
    '''
    Tester needs to occupy the cells that correspond to the cuts.
    '''
    sys_z = 'Z'
    sys_x = 'X'
    test_z = "env_z"
    test_x = "env_x"
    q_str = 'q'

    cut_specs = set()
    for cut in cuts:
        out_node = GD.node_dict[cut[0]]
        out_state = out_node[0]
        out_q = out_node[-1]
        in_node = GD.node_dict[cut[1]]
        in_state = in_node[0]
        system_state = '('+ sys_z + ' = ' + str(out_state[0]) + ' & ' + sys_x + ' = ' + str(out_state[1]) + ' & ' +q_str+' = '+str(out_q[1:])+')'
        block_state = '('+ test_z + ' = ' + str(in_state[0]) + ' & ' + test_x + ' = ' + str(in_state[1])+')'
        cut_specs |= { system_state + ' -> ' + block_state}

    return cut_specs

def do_not_excessively_constrain(GD, cuts):
    '''
    Do not constrain edges that are not cut.
    '''
    sys_z = 'Z'
    sys_x = 'X'
    test_z = "env_z"
    test_x = "env_x"
    q_str = 'q'

    do_not_overconstrain = set()
    for node in list(GD.nodes):
        out_node = GD.node_dict[node]
        out_state = out_node[0]
        out_q = out_node[-1]
        current_state = '('+sys_z+'= '+str(out_state[0])+' & '+sys_x+' = '+str(out_state[1])+' & '+q_str+' = '+str(out_q[1:])+')'
        state_str = ''
        edge_list = list(GD.graph.edges(node))
        for edge in edge_list:
            in_node = GD.node_dict[edge[1]]
            in_state = in_node[0]
            if edge not in cuts:
                state_str = state_str + '('+ test_z + ' = ' + str(in_state[0]) + ' & ' + test_x + ' = ' + str(in_state[1])+') || '

        if state_str != '':
            state_str = state_str[:-4]
            do_not_overconstrain |=  { current_state + ' -> !(' + state_str + ')'}

    return do_not_overconstrain

def turn_based():
    '''
    Only one agent can move at a time.
    turn 0 -> Tester's turn
    turn 1 -> System's turn
    '''
    sys_z = 'Z'
    sys_x = 'X'
    test_z = "env_z"
    test_x = "env_x"
    q_str = 'q'
    turn = 'turn'

    turn_spec = set()
    turn_spec |= {'('+turn+'= 0 -> X('+turn+'= 1)'}
    turn_spec |= {'('+turn+'= 1 -> X('+turn+'= 0)'}
    turn_spec |= {'('+turn+'= 0 & '+sys_z+' = X('+sys_z+') & '+sys_x+' = X('+sys_x+') & '+q_str+' = X('+q_str+'))'}
    turn_spec |= {'('+turn+'= 1 & '+test_z+' = X('+test_z+') & '+test_x+' = X('+test_x+'))'}

    return turn_spec
