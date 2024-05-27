'''
Defining the problem data for the example.
'''

MAZEFILE = 'maze.txt'

INIT = [(4,0)]
GOALS = [(0,4)]
INT = [(1,0)]
# UNSAFE = [(1,3)]
INT2 = [(2,2)]

INTS = {pos: 'I' for pos in INT}
#INTS.update({pos: 'D' for pos in UNSAFE})
INTS.update({pos: 'I_2' for pos in INT2})


SYS_FORMULA = 'F(goal) & G(I->X(X(X(I_2))))' # adding in globally always not unsafe, (expect system to do this on its own, system formula), safety (always avoid this state)
TEST_FORMULA = 'F(I)'
# TEST_FORMULA = 'F(I_2) & F(I)' # force system to do something with cuts = test formula, reachability spec

# intermediate state needs to be on the way to the goal to be feasible, for static 
