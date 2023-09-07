import pyomo.environ as pyo
from ipdb import set_trace as st

def add_static_obstacle_constraints_on_S(model, G, S):
    map_G_to_S = find_map_G_S(G,S)
    model = feasibility_vars_and_constraints(model, S, map_G_to_S)
    return model

def add_static_obstacle_constraints_on_G(model, GD): # only works for single tester flow
    G_truncated = {}
    for node in GD.node_dict:
        G_truncated.update({node: (str(GD.node_dict[node][0]))})

    flip_dict = {}
    for key in G_truncated.keys():
        if G_truncated[key] in flip_dict.keys():
            new_mapping = flip_dict[G_truncated[key]] + key
            flip_dict.update({G_truncated[key]: new_mapping})

    model.static_cut_cons = pyo.ConstraintList()
    edge_list = list(GD.graph.edges)

    for count,(i,j) in enumerate(edge_list):
        for (imap, jmap) in edge_list[count+1:]:
            if G_truncated[i] == G_truncated[imap] and G_truncated[j] == G_truncated[jmap]:
                expression = model.y['d', i, j] == model.y['d', imap, jmap]
                model.static_cut_cons.add(expr = expression)
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
