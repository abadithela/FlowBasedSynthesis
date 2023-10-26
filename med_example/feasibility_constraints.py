import pyomo.environ as pyo
from ipdb import set_trace as st

def add_static_obstacle_constraints(model, GD, SD):
    model = map_static_obstacles_to_G(model, GD)
    model = add_bidirectional_edge_cuts_on_G(model, GD)
    return model

def map_static_obstacles_to_G(model, GD):
    model.map_static_obstacles_to_G = pyo.ConstraintList()
    edge_list = list(model.edges)
    for count, (i,j) in enumerate(edge_list):
        out_state = GD.node_dict[i][0]
        in_state = GD.node_dict[j][0]
        for (imap,jmap) in edge_list[count:]:
            if out_state == GD.node_dict[imap][0] and in_state == GD.node_dict[jmap][0]:
                expression = model.d_aux[i, j] == model.d_aux[imap, jmap]
                model.map_static_obstacles_to_G.add(expr = expression)
    return model

def add_bidirectional_edge_cuts_on_G(model, GD):
    model.cut_edges_bidirectionally = pyo.ConstraintList()
    edge_list = list(model.edges)
    for count, (i,j) in enumerate(edge_list):
        out_state = GD.node_dict[i][0]
        in_state = GD.node_dict[j][0]
        for (imap,jmap) in edge_list[count+1:]:
            if in_state == GD.node_dict[imap][0] and out_state == GD.node_dict[jmap][0]:
                expression = model.d_aux[i, j] == model.d_aux[imap, jmap]
                model.cut_edges_bidirectionally.add(expr = expression)
    return model

def find_map_G_S(GD,SD):
    G_truncated = {}
    S_annot = {}
    map_G_to_S = {}
    for node in GD.node_dict:
        G_truncated.update({node: (str(GD.node_dict[node][0]))})
    for node in SD.node_dict:
        S_annot.update({node: (str(SD.node_dict[node][0]))})
    for node in G_truncated:
        for sys_node in S_annot:
            if G_truncated[node]  == S_annot[sys_node]:
                map_G_to_S.update({node: sys_node})
    # st()
    return map_G_to_S

def feasibility_vars_and_constraints(model, S, map_G_to_S):
    vars = ['fS']

    model.s_edges = S.edges
    model.s_nodes = S.nodes
    model.s_var = pyo.Var(vars, model.s_edges, within=pyo.NonNegativeReals)
    # model.s_p = pyo.Var(within=pyo.NonNegativeReals)
    src = S.init
    sink = S.acc_sys

    # Preserve flow of 1 in S
    def preserve_f_s(model):
        return model.t <= sum(model.s_var['fS', i,j] for (i, j) in model.s_edges if i in src)
    model.preserve_f_s = pyo.Constraint(rule=preserve_f_s)

    # Capacity constraint on flow
    def cap_constraint(model, i, j):
        return model.s_var['fS',  i, j] <= model.t
    model.cap_s = pyo.Constraint(model.s_edges, rule=cap_constraint)

    # Match the edge cuts from G to S
    def match_cut_constraints(model, i, j):
        imap = map_G_to_S[i]
        jmap = map_G_to_S[j]
        return model.s_var['fS', imap, jmap] + model.y['d', i, j] <= model.t
    model.de_cut = pyo.Constraint(model.edges, rule=match_cut_constraints)

    # Conservation constraints:
    def s_conservation(model,k):
        if k in src or k in sink:
            return pyo.Constraint.Skip
        incoming  = sum(model.s_var['fS',i,j] for (i,j) in model.s_edges if (j == k))
        outgoing = sum(model.s_var['fS', i,j] for (i,j) in model.s_edges if (i == k))
        return incoming == outgoing
    model.s_cons = pyo.Constraint(model.s_nodes, rule=s_conservation)

    # no flow into sources and out of sinks
    def s_no_in_source(model,i,k):
        if k in src:
            return model.s_var['fS',i,k] == 0
        else:
            return pyo.Constraint.Skip
    model.s_no_in_source = pyo.Constraint(model.s_edges, rule=s_no_in_source)

    # nothing leaves sink
    def s_no_out_sink(model,i,k):
        if i in sink:
            return model.s_var['fS',i,k] == 0
        else:
            return pyo.Constraint.Skip
    model.s_no_out_sink = pyo.Constraint(model.s_edges, rule=s_no_out_sink)

    return model

def add_feasibility_constraints(model, GD, SD): #assuming you can always go back to initial position
    '''
    Remember the history variable and check that for each q the system still has a path to the goal.
    '''
    map_G_to_S = find_map_G_S(GD,SD)

    # create G and remove self-loops
    S = SD.graph
    to_remove = []
    for i, j in S.edges:
        if i == j:
            to_remove.append((i,j))
    S.remove_edges_from(to_remove)

    node_list = []
    for node in GD.nodes:
        node_list.append(GD.node_dict[node])

    qs = list(set([node[-1] for node in node_list]))
    vars = ['fS_'+ str(q) for q in qs]

    src = SD.init
    sink = SD.acc_sys

    model.s_edges = S.edges
    model.s_nodes = S.nodes
    model.s_var = pyo.Var(vars, model.s_edges, within=pyo.NonNegativeReals)

    # feasibility constraint list
    model.feasibility = pyo.ConstraintList()

    for q in qs:

        # Match the edge cuts from G to S
        for (i,j) in model.edges:
            if GD.node_dict[i][-1] == q:
                imap = map_G_to_S[i]
                jmap = map_G_to_S[j]
                expression =  model.s_var['fS_'+ str(q), imap, jmap] + model.d_aux[i, j] <= 1
                model.feasibility.add(expr = expression)

        # Normal flow constraints
        # Preserve flow of 1 in S for each individual q
        expression =  1 <= sum(model.s_var['fS_'+ str(q), i,j] for (i, j) in model.s_edges if i in src)
        model.feasibility.add(expr = expression)

        # Capacity constraint on flow
        for (i,j) in model.s_edges:
            expression =  model.s_var['fS_'+ str(q),  i, j] <= 1
            model.feasibility.add(expr = expression)

        # Conservation constraints:
        for k in model.s_nodes:
            if k not in src and k not in sink:
                incoming  = sum(model.s_var['fS_'+ str(q),i,j] for (i,j) in model.s_edges if (j == k))
                outgoing = sum(model.s_var['fS_'+ str(q), i,j] for (i,j) in model.s_edges if (i == k))
                expression = incoming == outgoing
                model.feasibility.add(expr = expression)

        # no flow into sources and out of sinks
        for (i,j) in model.s_edges:
            if j in src:
                expression = model.s_var['fS_'+ str(q),i,j] == 0
                model.feasibility.add(expr = expression)

        # nothing leaves sink
        for (i,j) in model.s_edges:
            if i in sink:
                expression = model.s_var['fS_'+ str(q),i,k] == 0
                model.feasibility.add(expr = expression)

    # maybe just add incoming flow=outgoing flow for each intermediate in G??

    return model

def add_feasibility_constraints_for_each_q(model, GD, SD): #assuming you can always go back to initial position
    '''
    Remember the history variable and check that for each q the system still has a path to the goal.
    '''
    init = SD.init
    # st()
    GD_inter = [node for node in GD.acc_test if node not in GD.acc_sys]
    inter = [SD.inv_node_dict[(GD.node_dict[node][0], 'q0')] for node in GD_inter]
    # int = [SD.inv_node_dict[((3, 4), 'q0')]]

    qs_dict = {'q0': init, 'q3': inter, 'q1': init, 'q2': init}

    map_G_to_S = find_map_G_S(GD,SD)

    # create G and remove self-loops
    S = SD.graph
    to_remove = []
    for i, j in S.edges:
        if i == j:
            to_remove.append((i,j))
    S.remove_edges_from(to_remove)

    node_list = []
    for node in GD.nodes:
        node_list.append(GD.node_dict[node])

    qs = list(set([node[-1] for node in node_list]))
    vars = ['fS_'+ str(q)+str(num) for q in qs for num in range(len(qs_dict[q]))]



    sink = SD.acc_sys

    model.s_edges = S.edges
    model.s_nodes = S.nodes
    model.s_var = pyo.Var(vars, model.s_edges, within=pyo.NonNegativeReals)

    # feasibility constraint list
    model.feasibility = pyo.ConstraintList()

    for q in qs:
        src_list = qs_dict[q]
        l = 0
        for src in src_list:
            # Match the edge cuts from G to S
            for (i,j) in model.edges_without_I:
                if GD.node_dict[i][-1] == q:
                    imap = map_G_to_S[i]
                    jmap = map_G_to_S[j]
                    expression =  model.s_var['fS_'+ str(q)+str(l), imap, jmap] + model.d[i, j] <= 1
                    model.feasibility.add(expr = expression)

            # Normal flow constraints
            # st()
            # Preserve flow of 1 in S for each individual q
            expression =  1 <= sum(model.s_var['fS_'+ str(q)+str(l), i,j] for (i, j) in model.s_edges if i == src)
            model.feasibility.add(expr = expression)

            # Capacity constraint on flow
            for (i,j) in model.s_edges:
                expression =  model.s_var['fS_'+ str(q)+str(l),  i, j] <= 1
                model.feasibility.add(expr = expression)

            # Conservation constraints:
            for k in model.s_nodes:
                if k != src and k not in sink:
                    incoming  = sum(model.s_var['fS_'+ str(q)+str(l),i,j] for (i,j) in model.s_edges if (j == k))
                    outgoing = sum(model.s_var['fS_'+ str(q)+str(l), i,j] for (i,j) in model.s_edges if (i == k))
                    expression = incoming == outgoing
                    model.feasibility.add(expr = expression)

            # no flow into sources and out of sinks
            for (i,j) in model.s_edges:
                if j == src:
                    expression = model.s_var['fS_'+ str(q)+str(l),i,j] == 0
                    model.feasibility.add(expr = expression)

            # nothing leaves sink
            for (i,j) in model.s_edges:
                if i in sink:
                    expression = model.s_var['fS_'+ str(q)+str(l),i,k] == 0
                    model.feasibility.add(expr = expression)
            l = l + 1

    # maybe just add incoming flow=outgoing flow for each intermediate in G??

    return model

def advanced_feasibility_constraints(model, GD, SD):
    '''
    Make sure that if a state is reachable in the previous q, then the next q is reachable from there.
    '''
    # new initial position for each q!
    # if there is a flow to that I (under the previous q), then there needs to remain a flow to T for the next q
    # it is not allowed to cut off the I completely

    # first remember the order of qs and at which state they change (we only care about S->(I1->I2 any order)->T)
    # first check for q0 if I1 is reachable (if I2 is reachable)
    # lower bound the flow for the next q by 1 if the flow from the last q is at least 1
    # let's try flow conservation
    init = SD.init[0]
    int_1 = SD.inv_node_dict[((3, 4), 'q0')]
    int_2 = SD.inv_node_dict[((1, 0), 'q0')]
    goal = SD.acc_sys
    #
    # q_dict = {('q0', 'q3') : int_1, ('q0', 'q4'): int_2, ('q3','q2'): int_2, ('q4','q2'): int_1, ('q2', 'q6'): goal}
    qs_dict = {'q0': [(init, int_1), (init, int_2)], 'q3': [(int_1,int_2)], 'q4': [(int_2,int_1)], 'q2': [(int_1, goal), (int_2,goal)], 'q1': [], 'q5': [], 'q6':[], 'q7':[]}

    map_G_to_S = find_map_G_S(GD,SD)

    # create G and remove self-loops
    S = SD.graph
    to_remove = []
    for i, j in S.edges:
        if i == j:
            to_remove.append((i,j))
    S.remove_edges_from(to_remove)

    node_list = []
    for node in GD.nodes:
        node_list.append(GD.node_dict[node])

    qs = list(set([node[-1] for node in node_list]))
    # vars = ['fS_'+ str(q) for q in qs]
    vars = ['fS_q00', 'fS_q01', 'fS_q3', 'fS_q4', 'fS_q20', 'fS_q21']

    model.s_edges = S.edges
    model.s_nodes = S.nodes
    model.s_var = pyo.Var(vars, model.s_edges, within=pyo.NonNegativeReals)

    # feasibility constraint list
    model.adv_feasibility = pyo.ConstraintList()

    for q in qs:
        num_flows = len(qs_dict[q])
        if num_flows > 1:
            for flow_num in range(num_flows):
                src = qs_dict[q][flow_num][0]
                sink = qs_dict[q][flow_num][1]
                # Match the edge cuts from G to S(for that flow)
                for (i,j) in model.edges_without_I:
                    if GD.node_dict[i][-1] == q:
                        imap = map_G_to_S[i]
                        jmap = map_G_to_S[j]
                        expression =  model.s_var['fS_'+ str(q)+str(flow_num), imap, jmap] + model.d[i, j] <= 1
                        model.adv_feasibility.add(expr = expression)

                # Normal flow constraints
                # Preserve flow of 1 in S for each individual q
                # expression =  1 <= sum(model.s_var['fS_'+ str(q)+str(flow_num), i,j] for (i, j) in model.s_edges if i == src)
                # model.adv_feasibility.add(expr = expression)

                # Capacity constraint on flow
                for (i,j) in model.s_edges:
                    expression = model.s_var['fS_'+ str(q)+str(flow_num),  i, j] <= 1
                    model.adv_feasibility.add(expr = expression)

                # Conservation constraints:
                for k in model.s_nodes:
                    if k != src and k != sink:
                        incoming  = sum(model.s_var['fS_'+ str(q)+str(flow_num),i,j] for (i,j) in model.s_edges if (j == k))
                        outgoing = sum(model.s_var['fS_'+ str(q)+str(flow_num), i,j] for (i,j) in model.s_edges if (i == k))
                        expression = incoming == outgoing
                        model.adv_feasibility.add(expr = expression)

                # no flow into sources and out of sinks
                for (i,j) in model.s_edges:
                    if j == src:
                        expression = model.s_var['fS_'+ str(q)+str(flow_num),i,j] == 0
                        model.adv_feasibility.add(expr = expression)
                # st()
                # nothing leaves sink
                for (i,j) in model.s_edges:
                    if i == sink:
                        expression = model.s_var['fS_'+ str(q)+str(flow_num),i,j] == 0
                        model.adv_feasibility.add(expr = expression)

    # conserve the flow across each of the the qs in G (and in S)
    conserve_dict = {int_1 : [('fS_q00', 'fS_q3'), ('fS_q4', 'fS_q20')], int_2: [('fS_q01', 'fS_q4'), ('fS_q3', 'fS_q21')] }

    # conserve across qs
    for node in conserve_dict.keys():
        for flows in conserve_dict[node]:
            in_flow = flows[0]
            out_flow = flows[1]
            incoming  = sum(model.s_var[in_flow,i,j] for (i,j) in model.s_edges if (j == node))
            outgoing = sum(model.s_var[out_flow, i,j] for (i,j) in model.s_edges if (i == node))
            expression = incoming == outgoing
            model.feasibility.add(expr = expression)

    # preserve flow into the sink
    # Normal flow constraints
    # Preserve flow of 1 in S for each individual q
    expression =  1 <= sum(model.s_var['fS_q00', i,j] for (i, j) in model.s_edges if i in SD.init) + sum(model.s_var['fS_q01', i,j] for (i, j) in model.s_edges if i in SD.init)
    model.feasibility.add(expr = expression)

    return model
