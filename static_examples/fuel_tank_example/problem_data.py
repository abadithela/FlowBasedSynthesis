'''
Defining the problem data for the example.
'''

MAZEFILE = 'maze.txt'

MAX_FUEL = 10

INIT = [((4,0),MAX_FUEL)]
GOALS = [((0,0),k) for k in range(0,MAX_FUEL)]
unsafes = [((x,y),0) for x in range(0,5) for y in range(0,5)]

LOW_FUEL = []
for z in range(0,5):
    for x in range(0,5):
        for f in range(1,min(((z)+x-1), MAX_FUEL)):
            LOW_FUEL.append(((z,x),f))

LOW_FUEL = list(set(LOW_FUEL))

INTS = {pos: 'int' for pos in LOW_FUEL}
INTS.update({pos: 'unsafe' for pos in unsafes})

SYS_FORMULA = 'F(goal) & G(!(unsafe))'
TEST_FORMULA = 'F(int)'
