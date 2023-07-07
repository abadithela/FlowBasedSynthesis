"""
File to construct asynchronous product and synchronous product.
"""
import sys
import spot
from spot.jupyter import display_inline
import buddy
import pdb
from gridworld_specs import TranSys
spot.setup(show_default='.tvb')


def sync_prod(sys, aut):
    """
    Synchronous product between transition system T (TranSys object) and Automaton Aut.
    """
    # If the two automata do not have the same BDD dict, then
    # we cannot easily detect compatible transitions.
    bdict = aut.get_dict()
    if aut.get_dict() != bdict:
        raise RuntimeError("automata should share their dictionary")
    result = spot.make_twa_graph(bdict)
    result.copy_ap_of(left)
    result.copy_ap_of(right)

    return prod

def async_prod(left, right):
    bdict = left.get_dict()
    # If the two automata do not have the same BDD dict, then
    # we cannot easily detect compatible transitions.
    if right.get_dict() != bdict:
        raise RuntimeError("automata should share their dictionary")
    result = spot.make_twa_graph(bdict)
    result.copy_ap_of(left)
    result.copy_ap_of(right)
    # The list of output states for which we have not yet
    # computed the successors.  Items on this list are triplets
    # of the form (ls, rs, p) where ls,rs are the state number in
    # the left and right automata, and p is the state number if
    # the output automaton.
    todo = []
    sdict = {}
    pairs = []   # our array of state pairs
    # Transform a pair of state number (ls, rs) into a state number in
    # the output automaton, creating a new state if needed.  Whenever
    # a new state is created, we can add it to todo.
    def dst(ls, rs):
        pair = (ls, rs)
        p = sdict.get(pair)
        if p is None:
            p = result.new_state()
            sdict[pair] = p
            pairs.append(pair)
            todo.append((ls, rs, p))
        return p
    
    # Setup the initial state.  It always exists.
    result.set_init_state(dst(left.get_init_state_number(), 
                              right.get_init_state_number()))
    
    # The acceptance sets of the right automaton will be shifted by this amount
    shift = left.num_sets()
    # result.set_acceptance(shift + right.num_sets(), left.get_acceptance() | (right.get_acceptance() << shift))
    result.set_acceptance(shift + right.num_sets(),
                          left.get_acceptance() | (right.get_acceptance() << shift)) # Not sure if the and here means both acceptances.

    # Build all states and edges in the product
    while todo:
        print(todo)
        lsrc, rsrc, osrc = todo.pop()
        print("----------------------------------")
        print(f"new edge in todo: ({lsrc}, {rsrc}, {osrc})")
        
        for lt in left.out(lsrc):
            if lt.cond != buddy.bddfalse:
                result.new_edge(osrc, dst(lt.dst, rsrc), lt.cond, lt.acc)
                
        for rt in right.out(rsrc):
            pdb.set_trace()
            if rt.cond != buddy.bddfalse:
                result.new_edge(osrc, dst(lsrc, rt.dst), rt.cond, rt.acc << shift)
                # membership of this transitions to the new acceptance sets
        
        # Remember the origin of our states
        result.set_product_states(pairs)
        
        # Loop over all the properties we want to preserve if they hold in both automata
        # This ensures that the product of NBAs is an NBA
        for p in ('prop_universal', 'prop_complete', 'prop_weak', 'prop_inherently_weak', 
                  'prop_terminal', 'prop_stutter_invariant', 'prop_state_acc'):
            if getattr(left, p)() and getattr(right, p)():
                getattr(result, p)(True)
    return result, sdict

if __name__ == "__main__":
    # Specification Product:
    a1 = spot.translate('G(tank_light -> F(refuel))', 'Buchi', 'state-based', 'complete'); a1.show("v")
    a2 = spot.translate('G(!(empty))')
    p2, states = async_prod(a1,a2)

    # System:
    mazefile = "../gridworld/maze.txt"
    Sys = construct_sys(mazefile)

    # Virtual Product Graph:
    
