'''
needs to be updated
'''

import pyomo.environ as pyo
from ipdb import set_trace as st

def add_static_obstacle_constraints_on_S(model, GD, SD, initialize):
    model = map_static_obstacles_to_G(model, GD)
    model = add_bidirectional_edge_cuts_on_G(model, GD)
    return model

def map_static_obstacles_to_G(model, GD):
    model.map_static_obstacles_to_G = pyo.ConstraintList()
    edge_list = list(model.edges)
    for count, (i,j) in enumerate(edge_list):
        out_state = GD.node_dict[i][0]
        in_state = GD.node_dict[j][0]
        for (imap,jmap) in edge_list[count+1:]:
            if out_state == GD.node_dict[imap][0] and in_state == GD.node_dict[jmap][0]:
                expression = model.y['d', i, j] == model.y['d', imap, jmap]
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
                expression = model.y['d', i, j] == model.y['d', imap, jmap]
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
            if G_truncated[node] == S_annot[sys_node]:
                map_G_to_S.update({node: sys_node})
    return map_G_to_S

def preserve_flow_on_S(model, SD, map_G_to_S, initialize):
    '''
    preserve flow on S for static obstacles (history variable q does not matter)
    '''

    # create S and remove self-loops
    S = SD.graph
    to_remove = []
    for i, j in S.edges:
        if i == j:
            to_remove.append((i,j))
    S.remove_edges_from(to_remove)

    model.s_edges = S.edges
    model.s_nodes = S.nodes
    model.f_on_S = pyo.Var(model.s_edges, within=pyo.NonNegativeReals)
    # model.s_p = pyo.Var(within=pyo.NonNegativeReals)
    src = SD.init
    sink = SD.acc_sys

    # Preserve flow of 1 in S
    def preserve_f_s(model):
        return model.t <= sum(model.f_on_S[i,j] for (i, j) in model.s_edges if i in src)
    model.preserve_f_s = pyo.Constraint(rule=preserve_f_s)

    # Capacity constraint on flow
    def s_cap_constraint(model, i, j):
        return model.f_on_S[i, j] <= model.t
    model.cap_s = pyo.Constraint(model.s_edges, rule=s_cap_constraint)

    # Match the edge cuts from G to S
    def match_cut_constraints_to_s(model, i, j):
        imap = map_G_to_S[i]
        jmap = map_G_to_S[j]
        return model.f_on_S[imap, jmap] + model.y['d', i, j] <= model.t
    model.se_de_cut = pyo.Constraint(model.edges, rule=match_cut_constraints_to_s)

    # Conservation constraints:
    def s_conservation(model,k):
        if k in src or k in sink:
            return pyo.Constraint.Skip
        incoming  = sum(model.f_on_S[i,j] for (i,j) in model.s_edges if (j == k))
        outgoing = sum(model.f_on_S[i,j] for (i,j) in model.s_edges if (i == k))
        return incoming == outgoing
    model.s_cons = pyo.Constraint(model.s_nodes, rule=s_conservation)

    # no flow into sources and out of sinks
    def s_no_in_source(model,i,k):
        if k in src:
            return model.f_on_S[i,k] == 0
        else:
            return pyo.Constraint.Skip
    model.s_no_in_source = pyo.Constraint(model.s_edges, rule=s_no_in_source)

    # nothing leaves sink
    def s_no_out_sink(model,i,k):
        if i in sink:
            return model.f_on_S[i,k] == 0
        else:
            return pyo.Constraint.Skip
    model.s_no_out_sink = pyo.Constraint(model.s_edges, rule=s_no_out_sink)

    if initialize:
        pass

    return model


def add_feasibility_constraints(model, GD, SD):
    '''
    Remember the history variable and check all cuts for that q.
    '''
    map_G_to_S = find_map_G_S(GD,SD)

    node_list = []
    for node in GD.nodes:
        node_list.append(GD.node_dict[node])

    qs = list(set([node[-1] for node in node_list]))
    vars = ['fS_'+ str(q) for q in qs]

    src = SD.init
    sink = SD.acc_sys

    model.s_edges = SD.edges
    model.s_nodes = SD.nodes
    model.s_var = pyo.Var(vars, model.s_edges, within=pyo.NonNegativeReals)

    # feasibility constraint list
    model.feasibility = pyo.ConstraintList()

    for q in qs:

        # Match the edge cuts from G to S
        for (i,j) in model.edges:
            if GD.node_dict[i][-1] == q:
                imap = map_G_to_S[i]
                jmap = map_G_to_S[j]
                expression =  model.s_var['fS_'+ str(q), imap, jmap] + model.y['d_e', i, j] <= model.t
                model.feasibility.add(expr = expression)

        # Normal flow constraints
        # Preserve flow of 1 in S
        expression =  1 <= sum(model.s_var['fS_'+ str(q), i,j] for (i, j) in model.s_edges if i in src)
        model.feasibility.add(expr = expression)

        # Capacity constraint on flow
        for (i,j) in model.s_edges:
            expression =  model.s_var['fS_'+ str(q),  i, j] <= model.t
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

    return model
