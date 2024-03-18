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
        G_truncated.update({node: GD.node_dict[node][0]})
    for node in SD.node_dict:
        S_annot.update({node: SD.node_dict[node][0]})
    for node in G_truncated:
        for sys_node in S_annot:
            if G_truncated[node]  == S_annot[sys_node]:
                map_G_to_S.update({node: sys_node})

    return map_G_to_S

def find_map_G_S_w_fuel(GD,SD):
    # st()
    G_truncated = {}
    S_annot = {}
    map_G_to_S = {}
    for node in GD.node_dict:
        G_truncated.update({node: GD.node_dict[node][0]})
    # G_truncated = list(set(G_truncated))
    for node in SD.node_dict:
        S_annot.update({node: SD.node_dict[node][0]})
    # S_annot = list(set(S_annot))
    for node in G_truncated:
        sys_nodes = []
        for sys_node in S_annot:
            if G_truncated[node][0]  == S_annot[sys_node][0]:
                sys_nodes.append(sys_node)
        map_G_to_S.update({node: sys_nodes})
    # st()
    return map_G_to_S


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


def add_static_feasibility_constraints(model, GD, SD): #assuming you can always go back to initial position
    '''
    Check that the system still has a path to the goal (q does not matter as obstacles are static).
    '''

    GD_inter = [node for node in GD.acc_test if node not in GD.acc_sys]
    inter = [SD.inv_node_dict[(GD.node_dict[node][0], 'q0')] for node in GD_inter]

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

    vars = ['fS']

    sink = SD.acc_sys
    src = SD.init[0]

    model.s_edges = S.edges
    model.s_nodes = S.nodes
    model.s_var = pyo.Var(vars, model.s_edges, within=pyo.NonNegativeReals)

    # feasibility constraint list
    model.feasibility = pyo.ConstraintList()

    # Match the edge cuts from G to S
    for (i,j) in model.edges:
        imap = map_G_to_S[i]
        jmap = map_G_to_S[j]
        expression =  model.s_var['fS', imap, jmap] + model.d_aux[i, j] <= 1
        model.feasibility.add(expr = expression)

    # Normal flow constraints
    # Preserve flow of 1 in S for each individual q
    expression =  1 <= sum(model.s_var['fS', i,j] for (i, j) in model.s_edges if i == src)
    model.feasibility.add(expr = expression)

    # Capacity constraint on flow
    for (i,j) in model.s_edges:
        expression =  model.s_var['fS', i,j] <= 1
        model.feasibility.add(expr = expression)

    # Conservation constraints:
    for k in model.s_nodes:
        if k != src and k not in sink:
            incoming  = sum(model.s_var['fS',i,j] for (i,j) in model.s_edges if (j == k))
            outgoing = sum(model.s_var['fS',i,j] for (i,j) in model.s_edges if (i == k))
            expression = incoming == outgoing
            model.feasibility.add(expr = expression)

    # no flow into sources and out of sinks
    for (i,j) in model.s_edges:
        if j == src:
            expression = model.s_var['fS',i,j] == 0
            model.feasibility.add(expr = expression)

    # nothing leaves sink
    for (i,j) in model.s_edges:
        if i in sink:
            expression = model.s_var['fS',i,k] == 0
            model.feasibility.add(expr = expression)

    return model
