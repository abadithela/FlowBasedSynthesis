'''
Helper functions to set up spot formulae.
'''
import spot
try:
    from components.products import Product
except:
    from products import Product


def neg(formula):
    return spot.formula.Not(formula)

def conjunction(formula_list):
    return spot.formula.And(formula_list)

def disjunction(formula_list):
    return spot.formula.Or(formula_list)

def instant_pruned_sync_prod(system, aut):
    prod = Product(system, aut)
    prod.instant_pruned_sync_prod()
    return prod

def synchronous_product(system, aut):
    '''
    Compute the synchronous product of sys(TS) x aut(B).
    '''
    # prod = Product(system, aut)
    # prod.construct_labels()
    # prod.construct_transitions()
    # prod.prune_unreachable_nodes()

    prod = instant_pruned_sync_prod(system, aut)
    return prod
