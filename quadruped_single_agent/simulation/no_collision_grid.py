r"""Gridworld example, with no collisions.

Noninterleaving version, so partial information with
horizon of length 1.

The player is Moore (chooses its primed variable values after
the other player chooses its own, expressed with quantifiers as
`\E sys_primed: \A env_primed:`).

The player makes assumptions about its environment that require
no more than a Moore player as environment. This ensures that
the environment and system are decoupled in time, at the
granularity of 1 logic time step (discrete time, at the
sampling frequency assumed for the discrete-layer model).

The conjunct ` u' = x /\ v' = y ` could have otherwise been
` (u = x /\ v = y)' `, but that would prime the variables
`x` and `y`, which are the environment's environment,
thus demanding a Mealy environment (more coupled, bordering
circularity that gives rise to noncausality of the assembled
system).

The "plus one" refers to requiring:

```tla
controllable_preimage ==
    \E sys_primed: \A env_primed:
        /\ sys_action
        /\ env_action => target_states
```

where:

- `sys_action` is `aut.action['sys']` below

- `env_action` is `aut.action['env']` below

- `target_states` is (the BDD that describes the state predicate
  of) the set of states in the current iteration of the
  backward iteration of an attractor as a (least) fixpoint,
  starting from the empty set of states, and disjoining the
  eventual goal (what is in `[]<>`, or in `<>` for finite-duration
  reachability games).
"""
import functools as _ft
import textwrap as _tw

import omega.games.gr1 as _gr1
import omega.games.enumeration as _enum
import omega.symbolic.temporal as _trl


def solve_design_problem():
    """Synthesize a controller."""
    spec = gr1_specification()
    controller = synthesize_some_controller(spec)


def gr1_specification():
    """Return a temporal logic spec in the GR(1) fragment."""
    aut = _trl.Automaton()
    aut.declare_variables(
    	x=(1, 4),
    	y=(1, 3),
    	u=(1, 4),
    	v=(1, 3))
        # These are type hints *only*:
        # The solver uses them to pick number of bits for
        # representing each variable symbol.
        # The relevant conjuncts `x \in 1..4` in the
        # formulas are necessary.
    aut.varlist.update(
    	env=['u', 'v'],
    	sys=['x', 'y'])
    aut.players = ['env', 'sys']
    aut.init['env'] = r'u = 2 /\ v = 3'
    aut.init['sys'] = r'x = 3 /\ y = 1'
    # NOTE: domain constraints are necessary in
    # an untyped language
    aut.action['env'] = r'''
        (* domain constraints
        The methods `Automaton.type_action_for()`
        and `type_hint_for()` are relevant.
        *)
        /\ u \in 1..4
            (* abscissa *)
        /\ u' \in 1..4
        /\ v \in 1..3
            (* ordinate *)
        /\ v' \in 1..3

        (* `abs(u' - u) <= 1` *)
        /\ (-1 <= (u' - u))
        /\ ((u' - u) <= 1)

        (* `abs(v' - v) <= 1` *)
        /\ (-1 <= (v' - v))
        /\ ((v' - v) <= 1)

        (* no collision (model) *)
        /\ ~ (u = x /\ v = y)
        /\ ~ (u' = x /\ v' = y)
            (* Moore env suffices:
            some decoupling in time *)
        '''
    aut.action['sys'] = r'''
        /\ x \in 1..4
        /\ x' \in 1..4
        /\ y \in 1..3
        /\ y' \in 1..3

        (* `abs(x' - x) <= 1` *)
        /\ (-1 <= (x' - x))
        /\ ((x' - x) <= 1)

        (* `abs(y' - y) <= 1` *)
        /\ (-1 <= (y' - y))
        /\ ((y' - y) <= 1)

        (* can constrain to only vertical moves
        when adjacent, to avoid diagonal
        crossing: ensures sampling frequency
        suffices *)

        (* no collision (model) *)
        /\ ~ (x = u /\ y = v)
        /\ ~ (x' = u /\ y' = v)

        (* does *not* work to require:
        `~ (x = u /\ y = v)'`
        from a Moore machine, because in the
        controllable predecessor we get:
        `\E x', y':  \A u', v':  ~ (x' = u' /\ y' = v')`,
        which is `FALSE`, because the formula
        `\E a:  \A b:  a = b` is `FALSE`.
        (`\A b:  \E a:  a = b` is `TRUE`,
        which is a Mealy machine `Step(_)` operator).
        *)
        '''
    # nonblocking of same square:
    #
    # ```tla
    # abs(r) == IF r < 0 THEN -r ELSE r
    #
    # persistence_disjunct ==
    #     <>[] /\ abs(x - u) <= 1
    #          /\ abs(y - v) <= 1
    # ```
    aut.win['<>[]'] = aut.bdds_from(
        r''' (
        (* `abs(x - u) <= 1` *)
        /\ -1 <= (x - u)
        /\ (x - u) <= 1

        (* `abs(y - v) <= 1` *)
        /\ -1 <= (y - v)
        /\ (y - v) <= 1
        )
        ''')
    aut.win['[]<>'] = aut.bdds_from(
        r' x = 3 /\ y = 1 ')
    aut.qinit = r'\E \A'
    aut.moore = True
    aut.plus_one = True
    aut.bdd.configure(reordering = True)
    return aut


def synthesize_some_controller(
        aut):
    """Return a controller that implements the spec."""
    z, yij, xijk = _gr1.solve_streett_game(aut)
    if z == aut.bdd.false:
        print(
            'empty steady-state solution '
            '(without initial condition conjoined)')
    else:
        hline = 30 * '_'
        indent = 4 * '\x20'
        print(
            '*some* initial states exist for '
            'the steady-state behavior')
        closure = _closure(aut)
        expr = aut.to_expr(
            closure,
            show_dom=True)
        expr = _tw.indent(
            expr,
            prefix=3 * indent)
        print(_tw.dedent(f'''
            {hline}
            closure:
            \n{expr}
            {hline}
            '''))
        expr = aut.to_expr(
            z,
            care=closure,
            show_dom=True)
        expr = _tw.indent(
            expr,
            prefix=3 * indent)
        print(_tw.dedent(f'''
            {hline}
            z:
            \n{expr}
            {hline}
            '''))
    _gr1.make_streett_transducer(z, yij, xijk, aut)
    return _enum.action_to_steps(
        aut,
        env='env',
        sys='impl',
        qinit=aut.qinit)


def _closure(
        aut):
    r"""Return the closure states of a formula.

    The closure of a temporal formula `Formula` is the collection of
    behaviors (behavior = sequence of states, each state an
    assignment of values to all variable names)
    that at each point can be extended to satisfy `Formula`.

    The closure is a safety property.
    The closure here does not refer to the safety property itself
    (the collection of infinite behaviors), but to the
    state predicate (as a BDD) that describes it.

    If `closure_states` is this state predicate,
    then the closure is the temporal property:
    `Formula /\ []closure_states`.

    These states are those from which it is "still possible"
    to realize the liveness goals of `Formula`,
    without violating the safety part.

    This function computes the closure for what is *assumed*
    to be the intended assembled system.


    ## Open systems and closure

    The closure of the open-system formula differs:
    for example a behavior where the system satisfies its
    initial condition and for `(n + 1)` steps its action,
    and the environment its initial condition and for
    `n` steps its action, is a behavior that satisfies
    the open-system formula (and so its closure).

    Nonetheless, for assemblies where the open-system is
    defined using the operator `Unzip(P, ...)`, where `P` is
    a closed-system formula, working with the closed-system
    does correspond to behaviors throughout which neither
    environment nor system violate their actions nor
    initial conditions (the env_action, sys_action,
    env_init, sys_init).

    The main feature when decomposing with `Unzip` is
    that if `P` has the form (where `[...]_vars` means
    `(vars' = vars) \/ ...` and is used for time-refinement)

    ```tla
    P ==
        /\ init
        /\ [][action]_vars
        /\ liveness
    ```

    then `Action` is (roughly) decomposed by projection:

    ```tla
    env_action ==
        [\E sys_vars': action]_(env_vars)
    sys_projection ==
        [\E env_vars': action]_(sys_vars)
    sys_action ==
        /\ sys_projection
        /\ \A env_vars':
            env_action => [action]_vars
    ```

    When `action` is intended to be the conjunction
    `aut.action['env'] & aut.action['sys']`,
    then the subformula `env_action => [action]_vars`
    can be omitted above. Usually this is the case,
    which is why starting with `P` (writing it and not
    `env_action` and `sys_action`), and computing from
    `P` the actions used for game solving avoids
    having to split the safety formulas.

    The `action` though should be of the *closure* of `P`,
    *not* of `P`, unless it so happens that the subformula
    of `init /\ [][action]_vars` already is the closure of
    `P`. This is why computing the closure is necessary
    when "opening" systems using `Unzip()`.

    Liveness subformulas []<> and <>[] in all cases
    constrain only the system (i.e., they can be
    placed in what resembles a consequent inside the
    open-system formula).

    That `P` "is a closed-system formula" means that
    `P` implies type hints for all variables that occur
    in `P`, i.e., it is a

    ```tla
    THEOREM
        P => [](x \in S /\ ...)
    ```

    where `x` ... are the variables occurring in `P`.

    When decomposing hierarchically into more than
    two components, then at some nodes in the decomposition
    graph, `P` in `Unzip(P)` will be an open system,
    not a closed one.

    The reason is that *that* node is about component A
    and component B, whose assembly is described by `P`.
    *But*, component C is assembled with A and B at
    another node, higher in the decomposition tree.

    So in formula `P`, component C is part of the
    environment of the assembled A and B.

    In this case, `P` itself is `Unzip(Q)`,
    `P == Unzip(Q)`, where `Q` describes the
    assembly of all three components A, B, and C.

    So the open-system at that node is `Unzip(Unzip(Q))`.

    It seems reasonable to expect that for `Q` of
    the conjunctive form described above (there for `P`),
    the actions `sys_action` and `next_action` for
    game solving to implement `Unzip(Unzip(Q))` would
    be computed by iterated projection, which would be
    flattened to projecting out variables of other
    players (this needs proving).
    """
    assembly = _trl.Automaton()
    env_init = aut.init['env']
    sys_init = aut.init['sys']
    init = env_init & sys_init
    action = aut.action['env'] & aut.action['sys']
    vrs = aut.vars_of_all_players
    type_hints = {
        name: aut.vars[name]['dom']
        for name in vrs}
    assembly.declare(**type_hints)
    assembly.varlist.update(
        env=list(),
        sys=vrs)
        # same as `omega.symbolic.temporal.conj_actions_of()`
    persistence_goals = aut.win['<>[]']
    recurrence_goals = aut.win['[]<>']
    assembly.action['env'] = aut.true
    assembly.action['sys'] = action
    assembly.init['env'] = aut.true
    assembly.init['sys'] = init
    assembly.win['<>[]'] = persistence_goals
    assembly.win['[]<>'] = recurrence_goals
    live_states, _, _ = _gr1.solve_streett_game(aut)
        # `z` describes the states winning for the
        # steady-state constraints, without initial condition
    reachable_states = _reachable_states(
        init, action, vrs, aut)
    diff = live_states & ~ reachable_states
    expr = aut.to_expr(diff)
    print(expr)
    return live_states & reachable_states


def _reachable_states(
        init,
        action,
        vrs,
        aut):
    """Return set of states reachable from `init`."""
    def operator(y):
        return _image(y, action, vrs, aut)
    return _least_fixpoint(operator, init)


def _image(
        source,
        action,
        vrs,
        aut):
    """Successors from `source` under `action`."""
    u = source & action
    u = aut.exist(vrs, u)
    return aut.replace_with_unprimed(vrs, u)


def _least_fixpoint(
        operator,
        target):
    """Least fixpoint of `operator`, starting from `target`."""
    y = target
    yold = None
    while y != yold:
        yold = y
        y |= operator(y)
    return y


if __name__ == '__main__':
    solve_design_problem()
